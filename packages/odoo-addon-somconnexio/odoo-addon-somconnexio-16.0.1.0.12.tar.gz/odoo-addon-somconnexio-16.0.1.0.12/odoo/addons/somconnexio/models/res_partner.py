from odoo import _, models, fields, api
from odoo.exceptions import ValidationError, UserError

from ..helpers.vat_normalizer import VATNormalizer
from ..helpers.bank_utils import BankUtils


class ResPartner(models.Model):
    _inherit = "res.partner"

    volunteer = fields.Boolean(string="Volunteer")

    type = fields.Selection(
        [
            ("contract-email", "Contract Email"),
            ("service", "Service Address"),
            ("invoice", "Invoice address"),
            ("delivery", "Shipping address"),
            ("other", "Other address"),
            ("representative", "Representative"),
        ],
        string="Address Type",
        default="representative",
    )
    nationality = fields.Many2one("res.country", "Nacionality")

    contract_ids = fields.One2many(
        string="Contracts", comodel_name="contract.contract", inverse_name="partner_id"
    )
    full_street = fields.Char(compute="_compute_full_street", store=True)
    mail_activity_count = fields.Integer(
        compute="_compute_mail_activity_count", string="Activity Count"
    )
    has_active_contract = fields.Boolean(
        string="Has active contract",
        compute="_compute_active_contract",
        store=True,
        readonly=True,
    )
    has_lead_in_provisioning = fields.Boolean(
        string="Has service in provisioning",
        compute="_compute_lead_in_provisioning",
        readonly=True,
    )

    only_indispensable_emails = fields.Boolean()

    banned_action_tags = fields.Many2many(
        "partner.action.tag",
        column1="partner_id",
        column2="action_tag_id",
        string="Banned actions",
    )

    @api.depends(
        "opportunity_ids.stage_id",
        "opportunity_ids.lead_line_ids",
    )
    def _compute_lead_in_provisioning(self):
        provisioning_crm_stages = [
            self.env.ref("crm.stage_lead1"),  # New
            self.env.ref("crm.stage_lead3"),  # Remesa
            self.env.ref("crm.stage_lead4"),  # Won
        ]
        for record in self:
            crm_in_provisioning = record.opportunity_ids.filtered(
                lambda cl: cl.stage_id in provisioning_crm_stages
            )
            record.has_lead_in_provisioning = bool(crm_in_provisioning)

    inactive_partner = fields.Boolean(
        string="Inactive Partner",
        compute="_compute_inactive_partner",
        readonly=True,
    )

    @api.depends("has_lead_in_provisioning", "has_active_contract")
    def _compute_inactive_partner(self):
        for partner in self:
            partner.inactive_partner = (
                not partner.has_active_contract and not partner.has_lead_in_provisioning
            )

    def _compute_mail_activity_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search(
            [('id', 'child_of', self.ids)]
        )
        mail_activities = {
            read['partner_id'][0]: read['partner_id_count']
            for read in self.env['mail.activity']._read_group(
                domain=[('partner_id', 'in', all_partners.ids)],
                fields=['partner_id'],
                groupby=['partner_id'],
            )
        }
        for record in self:
            record.mail_activity_count = mail_activities.get(record.id, 0)
    # UNCOMMENT Pending of review if is needed
    #    @api.model
    #    def _name_search(
    #        self, name, args=None, operator='ilike', limit=100, name_get_uid=None
    #    ):
    #        if ['parent_id', '=', False] in args:
    #            search_not_children = True
    #        else:
    #            search_not_children = False
    #        args = [
    #            arg for arg in args
    #            if arg != ['is_customer', '=', True] and arg != ['parent_id', '=', False]  # noqa
    #        ]
    #        result = super()._name_search(
    #            name=name, args=args, operator=operator,
    #            limit=limit, name_get_uid=name_get_uid
    #        )
    #        partner_ids = []
    #        for r in result:
    #            partner = self.browse(r)
    #            if search_not_children and partner.parent_id:
    #                continue
    #            if partner.type == 'contract-email':
    #                partner_id = partner.parent_id.id
    #            else:
    #                partner_id = partner.id
    #            partner_ids.append(partner_id)
    #        if partner_ids:
    #            partner_ids = list(set(partner_ids))
    #            result = partner_ids
    #        else:
    #            result = []
    #        return result

    def get_mandate(self, sanitized_iban):
        mandate = self.env.get("account.banking.mandate").search(
            [
                ("state", "=", "valid"),
                ("partner_id", "=", self.id),
                ("partner_bank_id.sanitized_acc_number", "=", sanitized_iban),
            ]
        )
        if mandate:
            return mandate[0]
        else:
            raise UserError(
                _("Partner id %s without mandate with acc %s")
                % (self.id, sanitized_iban)
            )

    def get_or_create_contract_email(self, email):
        if not email:
            return self

        email_partner_id = (
            self.env["res.partner"]
            .sudo()
            .search(
                [
                    ("email", "=", email),
                    "|",
                    ("id", "=", self.id),
                    "&",
                    ("parent_id", "=", self.id),
                    ("type", "=", "contract-email"),
                ],
                limit=1,
            )
        )

        if email_partner_id:
            return email_partner_id

        # If we can't find the email in the partner or its child contacts, create it
        # as a child partner with type 'contract-email'.
        new_email_partner_id = (
            self.env["res.partner"]
            .sudo()
            .create(
                {
                    "name": self.name,
                    "email": email,
                    "parent_id": self.id,
                    "type": "contract-email",
                }
            )
        )
        return new_email_partner_id

    def get_available_emails(self):
        self.ensure_one()
        email_list = self.env["res.partner"].search(
            [("parent_id", "=", self.id), ("type", "=", "contract-email")]
        )

        emails = set([e.email for e in email_list])
        if self.email and self.email not in emails:
            email_list = email_list | self

        return email_list

    def get_available_email_ids(self):
        self.ensure_one()
        email_id_list = [self.id] if self.email else []
        email_id_obj = self.env["res.partner"].search(
            [("parent_id", "=", self.id), ("type", "=", "contract-email")]
        )
        for data in email_id_obj:
            email_id_list.append(data.id)
        return email_id_list

    def _get_name(self):
        # UNCOMMENT. Review the self structure
        if self.type == "contract-email":
            return self.email
        if self.type == "service":
            self.name = dict(self.fields_get(["type"])["type"]["selection"])[self.type]
        res = super()._get_name()
        return res

    @api.constrains("child_ids")
    def _check_invoice_address(self):
        invoice_addresses = self.env["res.partner"].search(
            [("parent_id", "=", self.id), ("type", "=", "invoice")]
        )
        if len(invoice_addresses) > 1:
            raise ValidationError(
                _("More than one Invoice address by partner is not allowed")
            )

    def _set_contract_emails_vals(self, vals):
        new_vals = {}
        if "parent_id" in vals:
            new_vals["parent_id"] = vals["parent_id"]
        if "email" in vals:
            new_vals["email"] = vals["email"]
        new_vals["type"] = "contract-email"
        new_vals["is_customer"] = False
        return new_vals

    @api.depends("street", "street2")
    def _compute_full_street(self):
        for record in self:
            if record.street2:
                record.full_street = "{} {}".format(record.street, record.street2)
            else:
                record.full_street = record.street

    @api.depends("contract_ids.is_terminated")
    def _compute_active_contract(self):
        for record in self:
            contracts = self.env["contract.contract"].search(
                [
                    ("partner_id", "=", record.id),
                    ("is_terminated", "=", False),
                ]
            )
            if not contracts:
                record.has_active_contract = False
            if any(not contract.is_terminated for contract in contracts):
                record.has_active_contract = True

    @api.constrains("vat")
    def _check_vat(self):
        for partner in self:
            vat = VATNormalizer(partner.vat).normalize()

            domain = [
                "|",
                ("vat", "=", vat),
                ("vat", "=", VATNormalizer(vat).convert_spanish_vat()),
            ]
            if partner.parent_id:
                domain += [
                    ("id", "!=", partner.parent_id.id),
                    ("id", "!=", partner.id),
                    "|",
                    ("parent_id", "!=", partner.parent_id.id),
                    ("parent_id", "=", False),
                ]
            else:
                domain += [
                    ("id", "!=", partner.id),
                    ("parent_id", "=", False),
                ]
            existing_vats = self.env["res.partner"].search(domain)
            if existing_vats:
                raise ValidationError(
                    _("A partner with VAT %s already exists in our system") % vat
                )

    @api.model
    def create(self, vals):
        if not (vals.get("ref") or vals.get("parent_id")):
            vals["ref"] = self.env.ref("somconnexio.sequence_partner").next_by_id()

        if "type" in vals and vals["type"] == "contract-email":
            vals = self._set_contract_emails_vals(vals)
        elif "type" in vals and vals["type"] == "invoice":
            raise UserError(_("Invoice addresses should not be used anymore"))
        if "vat" in vals:
            vals["vat"] = VATNormalizer(vals["vat"]).normalize()

            existing_vats = self.env["res.partner"].search(
                [
                    "|",
                    ("vat", "=", vals["vat"]),
                    ("vat", "=", VATNormalizer(vals["vat"]).convert_spanish_vat()),
                ]
            )
            if existing_vats:
                raise UserError(
                    _("A partner with VAT %s already exists in our system")
                    % vals["vat"]
                )
        bank_ids = vals.get("bank_ids")
        if bank_ids:
            iban_to_validate = BankUtils.extract_iban_from_list(bank_ids)

            if iban_to_validate:
                BankUtils.validate_iban(iban_to_validate, self.env)

        return super().create(vals)

    def write(self, vals):
        if "vat" in vals:
            vals["vat"] = VATNormalizer(vals["vat"]).normalize()
        bank_ids = vals.get("bank_ids")
        if bank_ids:
            iban_to_validate = BankUtils.extract_iban_from_list(bank_ids)

            if iban_to_validate:
                BankUtils.validate_iban(iban_to_validate, self.env)

        if "type" in vals and vals["type"] == "contract-email":
            vals = self._set_contract_emails_vals(vals)
            for partner in self:
                partner.name = False
                partner.street = False
                partner.street2 = False
                partner.city = False
                partner.state_id = False
                partner.country_id = False
                partner.is_customer = False
        address_fields_str = ["street", "street2", "zip", "city"]
        address_fields_obj = {
            "state_id": "res.country.state",
            "country_id": "res.country",
        }
        message_template = _("Contact address has been changed from {} to {}")
        messages = {}
        for partner in self:
            messages[partner.id] = [
                message_template.format(partner[field], vals[field])
                for field in vals
                for address_field in address_fields_str
                if field == address_field and vals[field] != partner[field]
            ]
            messages[partner.id] += [
                message_template.format(
                    partner[field].name,
                    self.env[address_fields_obj[field]].browse(vals[field]).name,
                )
                for field in vals
                for address_field in address_fields_obj
                if field == address_field and vals[field] != partner[field].id
            ]

        super().write(vals)
        for partner in self:
            for message in messages[partner.id]:
                partner.message_post(message)
        return True

    def _invoice_state_action_view_partner_invoices(self):
        """Return a list of states to filter the invoices with operator 'not in'"""
        return ["cancel"]

    # Override this method of account to modify the invoice states used to filter
    # the invoices to show.
    # This code can be moved to the original account model.
    def action_view_partner_invoices(self):
        action = super().action_view_partner_invoices()
        domain = action["domain"]
        domain = [rule for rule in domain if rule[0] != "state"]
        domain.append(
            ("state", "not in", self._invoice_state_action_view_partner_invoices())
        )
        action["domain"] = domain
        return action

    def _construct_constraint_msg(self, country_code):
        # This method overrides the one from base_vat module to get adequate translation
        # and removes funcionality we were not using
        # https://github.com/OCA/OCB/blob/14.0/addons/base_vat/models/res_partner.py
        return "\n" + _(
            "The VAT number {vat} for partner {name} does not seem to be valid. \n"
            "Note: Expected format for DNI is ESXXXXXXXX [Letter], for NIE is ES [Letter] XXXXXXX [Letter]"  # noqa
        ).format(
            vat=self.vat,
            name=self.name,
        )

    @api.constrains("active")
    def _contrains_active(self):
        if not self.active and not self.env.user.has_group("base.group_system"):
            raise UserError(_("You cannot archive contacts"))
