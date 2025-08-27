import logging
import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..helpers.bank_utils import BankUtils

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = "crm.lead"

    skip_duplicated_phone_validation = fields.Boolean(
        string="Skip duplicated phone validation",
    )

    partner_category_id = fields.Many2many(
        "res.partner.category",
        string="Tags",
        related="partner_id.category_id",
    )
    create_date = fields.Datetime("Creation Date")

    mobile_lead_line_ids = fields.One2many(
        "crm.lead.line",
        string="Mobile lead lines",
        compute="_compute_mobile_lead_line_ids",
    )

    broadband_lead_line_ids = fields.One2many(
        "crm.lead.line",
        string="BA lead lines",
        compute="_compute_broadband_lead_line_ids",
    )

    has_mobile_lead_lines = fields.Boolean(
        compute="_compute_has_mobile_lead_lines", store=True
    )
    has_broadband_lead_lines = fields.Boolean(
        compute="_compute_has_broadband_lead_lines", store=True
    )
    broadband_wo_fix_lead_line_ids = fields.One2many(
        "crm.lead.line",
        string="BA without fix lead lines",
        compute="_compute_broadband_wo_fix_lead_line_ids",
    )
    broadband_w_fix_lead_line_ids = fields.One2many(
        "crm.lead.line",
        string="BA with fix lead lines",
        compute="_compute_broadband_w_fix_lead_line_ids",
    )
    phones_from_lead = fields.Char(compute="_compute_phones_from_lead", store=True)
    email_sent = fields.Boolean()
    is_broadband_isp_info_type_location_change = fields.Boolean(
        compute="_compute_is_broadband_isp_info_type_location_change"
    )

    def _ensure_crm_lead_iban_belongs_to_partner(self, crm_lead):
        partner_iban_list = crm_lead.partner_id.bank_ids.mapped("sanitized_acc_number")
        crm_lead_iban_list = crm_lead.lead_line_ids.mapped("iban")

        # IBANS present in CRM Lead Lines but not found with their partner
        missing_ibans = [
            iban
            for iban in crm_lead_iban_list
            if iban and iban not in partner_iban_list
        ]
        for iban in missing_ibans:
            self.env["res.partner.bank"].create(
                {
                    "acc_type": "iban",
                    "acc_number": iban,
                    "partner_id": crm_lead.partner_id.id,
                }
            )

    def action_set_won(self):
        for crm_lead in self:
            crm_lead.validate_won()
            crm_lead.validate_icc()
            if crm_lead.lead_line_ids.mapped("iban"):
                self._ensure_crm_lead_iban_belongs_to_partner(crm_lead)
        super(CrmLead, self).action_set_won()

    def validate_won(self):
        if self.stage_id != self.env.ref("crm.stage_lead3"):
            raise ValidationError(
                _("The crm lead must be in remesa or delivery generated stage.")
            )

    def validate_icc(self):
        for line in self.lead_line_ids.filtered("is_mobile"):
            if not line.mobile_isp_info.icc:
                raise ValidationError(
                    _("The ICC value of all mobile lines is not filled")
                )
            icc_prefix = self.env["ir.config_parameter"].get_param(
                "somconnexio.icc_start_sequence"
            )
            if (
                not line.mobile_isp_info.icc.startswith(icc_prefix)
                or len(line.mobile_isp_info.icc) != 19
            ):
                raise ValidationError(
                    _(
                        "The value of ICC is not right: it must contain "
                        "19 digits and starts with {}"
                    ).format(icc_prefix)
                )

    @api.depends("lead_line_ids")
    def _compute_mobile_lead_line_ids(self):
        for crm in self:
            crm.mobile_lead_line_ids = crm.lead_line_ids.filtered(lambda p: p.is_mobile)

    @api.depends("mobile_lead_line_ids")
    def _compute_has_mobile_lead_lines(self):
        for crm in self:
            crm.has_mobile_lead_lines = bool(crm.mobile_lead_line_ids)

    @api.depends("lead_line_ids")
    def _compute_broadband_lead_line_ids(self):
        for crm in self:
            crm.broadband_lead_line_ids = crm.lead_line_ids.filtered(
                lambda p: p.is_4G or p.is_adsl or p.is_fiber
            )

    @api.depends("broadband_lead_line_ids")
    def _compute_has_broadband_lead_lines(self):
        for crm in self:
            crm.has_broadband_lead_lines = bool(crm.broadband_lead_line_ids)

    @api.depends("broadband_lead_line_ids")
    def _compute_broadband_wo_fix_lead_line_ids(self):
        for record in self:
            record.broadband_wo_fix_lead_line_ids = (
                record.broadband_lead_line_ids.filtered(
                    lambda l: (l.product_id.without_fix)
                )
            )

    @api.depends("broadband_lead_line_ids")
    def _compute_broadband_w_fix_lead_line_ids(self):
        for record in self:
            record.broadband_w_fix_lead_line_ids = (
                record.broadband_lead_line_ids.filtered(
                    lambda l: (not l.is_mobile and not l.product_id.without_fix)
                )
            )

    @api.depends("lead_line_ids")
    def _compute_phones_from_lead(self):
        for crm in self:
            mbl_phones = crm.mobile_lead_line_ids.mapped("mobile_isp_info_phone_number")
            ba_phones = crm.broadband_lead_line_ids.filtered(
                lambda l: (
                    l.broadband_isp_info_phone_number
                    and l.broadband_isp_info_phone_number != "-"
                )
            ).mapped("broadband_isp_info_phone_number")
            crm.phones_from_lead = mbl_phones + ba_phones

    def _get_email(self, vals):
        if vals.get("partner_id"):
            return self.env["res.partner"].browse(vals.get("partner_id")).email

    @api.model
    def create(self, vals):
        if not vals.get("email_from"):
            vals["email_from"] = self._get_email(vals)
        leads = super(CrmLead, self).create(vals)
        return leads

    def action_set_paused(self):
        paused_stage_id = self.env.ref("crm.stage_lead2").id
        for crm_lead in self:
            crm_lead.write({"stage_id": paused_stage_id})

    def action_set_remesa(self):
        remesa_stage_id = self.env.ref("crm.stage_lead3").id
        for crm_lead in self:
            crm_lead.validate_remesa()
            crm_lead.write({"stage_id": remesa_stage_id})

    def action_set_cancelled(self):
        cancelled_stage_id = self.env.ref("somconnexio.stage_lead5").id
        for crm_lead in self:
            crm_lead.write({"stage_id": cancelled_stage_id, "probability": 0})

    def action_send_email(self):
        for crm_lead in self:
            template = crm_lead.with_context(
                lang=crm_lead.partner_id.lang
            )._get_crm_lead_creation_email_template()

            template.sudo().send_mail(crm_lead.id)
            crm_lead.email_sent = True

    def validate_remesa(self):
        self.ensure_one()
        # Check if related SR is validated
        if not self.partner_id:
            raise ValidationError(
                _("Error in {}: No partner to validate.").format(self.id)
            )
        for iban in self.lead_line_ids.mapped("iban"):
            BankUtils.validate_iban(iban, self.env)

        # Validate phone number
        self._validate_phone_number()

        if self.stage_id != self.env.ref("crm.stage_lead1"):
            raise ValidationError(_("The crm lead must be in new stage."))

    def _phones_already_used(self, line):
        # Avoid phone duplicity validation with address change leads
        if line.create_reason == "location_change":
            self.skip_duplicated_phone_validation = True

        if self.skip_duplicated_phone_validation:
            return False

        phone = False
        if line.mobile_isp_info:
            phone = line.mobile_isp_info.phone_number
        else:
            phone = line.broadband_isp_info.phone_number
        if not phone or phone == "-":
            return False
        contracts = self.env["contract.contract"].search(
            [
                ("is_terminated", "=", False),
                "|",
                "|",
                "|",
                ("mobile_contract_service_info_id.phone_number", "=", phone),
                ("vodafone_fiber_service_contract_info_id.phone_number", "=", phone),
                ("mm_fiber_service_contract_info_id.phone_number", "=", phone),
                ("adsl_service_contract_info_id.phone_number", "=", phone),
            ]
        )
        won_stage_id = self.env.ref("crm.stage_lead4").id
        remesa_stage_id = self.env.ref("crm.stage_lead3").id
        new_stage_id = self.env.ref("crm.stage_lead1").id
        order_lines = self.env["crm.lead.line"].search(
            [
                "|",
                ("lead_id.stage_id", "=", won_stage_id),
                ("lead_id.stage_id", "=", remesa_stage_id),
                "|",
                ("mobile_isp_info.phone_number", "=", phone),
                ("broadband_isp_info.phone_number", "=", phone),
            ]
        )
        if contracts or order_lines:
            raise ValidationError(
                _(
                    "Error in {}: Contract or validated CRMLead with the same phone already exists."  # noqa
                ).format(self.id)
            )
        new_lines = self.env["crm.lead.line"].search(
            [
                ("lead_id.stage_id", "=", new_stage_id),
                "|",
                ("mobile_isp_info.phone_number", "=", phone),
                ("broadband_isp_info.phone_number", "=", phone),
            ]
        )
        if len(new_lines) > 1:
            raise ValidationError(
                _("Error in {}: Duplicated phone number in CRMLead petitions.").format(
                    self.id
                )  # noqa
            )

    def _phone_number_portability_format_validation(self, line):
        if (
            line.mobile_isp_info_type == "portability"
            or line.broadband_isp_info_type == "portability"
        ):  # noqa
            phone = (
                line.mobile_isp_info_phone_number
                or line.broadband_isp_info_phone_number
            )  # noqa
            if not phone:
                raise ValidationError(_("Phone number is required in a portability"))
            pattern = None
            if line.mobile_isp_info:
                pattern = re.compile(r"^(6|7)?[0-9]{8}$")
                message = _(
                    "Mobile phone number has to be a 9 digit number starting with 6 or 7"  # noqa
                )
            elif not line.check_phone_number:
                pattern = re.compile(r"^(8|9)?[0-9]{8}$|^-$")
                message = _(
                    'Landline phone number has to be a dash "-" or a 9 digit number starting with 8 or 9'  # noqa
                )

            isValid = pattern.match(phone) if pattern else True
            if not isValid:
                raise ValidationError(message)

    def _validate_phone_number(self):
        self.ensure_one()
        for line in self.lead_line_ids:
            self._phone_number_portability_format_validation(line)
            self._phones_already_used(line)

    def action_set_new(self):
        for lead in self:
            new_stage_id = self.env.ref("crm.stage_lead1")
            lead.write({"stage_id": new_stage_id.id})

    def action_restore(self):
        for lead in self:
            lead.toggle_active()
            new_stage_id = self.env.ref("crm.stage_lead1")
            lead.write({"stage_id": new_stage_id.id})

    def _get_crm_lead_creation_email_template(self):
        return self.env.ref("somconnexio.crm_lead_creation_manual_email_template")

    @api.depends("broadband_lead_line_ids")
    def _compute_is_broadband_isp_info_type_location_change(self):
        for record in self:
            record.is_broadband_isp_info_type_location_change = any(
                line.broadband_isp_info.type == "location_change"
                for line in record.lead_line_ids
                if line.broadband_isp_info
            )
