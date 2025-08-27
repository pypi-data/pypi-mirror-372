from datetime import date, timedelta
from odoo import models, fields, api, _


class ContractHolderChangeWizard(models.TransientModel):
    _name = "contract.holder.change.wizard"
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=True,
    )
    contract_id = fields.Many2one("contract.contract")
    change_date = fields.Date("Change Date", required=True)
    payment_mode = fields.Many2one(
        "account.payment.mode",
        string="Payment mode",
        required=True,
    )
    banking_mandate_required = fields.Boolean(
        related="payment_mode.payment_method_id.bank_account_required"
    )
    available_banking_mandates = fields.Many2many(
        "account.banking.mandate",
        compute="_compute_available_banking_mandates",
        default=False,
    )
    banking_mandate_id = fields.Many2one(
        "account.banking.mandate",
        string="Banking mandate",
    )
    email_ids = fields.Many2many(
        "res.partner",
        string="Emails",
        required=True,
    )
    available_email_ids = fields.Many2many(
        "res.partner",
        string="Available Emails",
        compute="_compute_available_email_ids",
        default=False,
    )
    notes = fields.Text(
        string="Notes",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
    )
    available_products = fields.Many2many(
        "product.product", compute="_compute_available_products", default=False
    )
    is_pack = fields.Boolean(
        related="contract_id.is_pack",
    )
    is_mobile = fields.Boolean(
        related="contract_id.is_mobile",
    )
    change_all_contracts_from_pack = fields.Selection(
        string="Which holder changes you want to make?",
        selection=[
            ("no", _("Only this contract")),
            ("yes", _("All contracts in pack")),
        ],
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        contract = self.env["contract.contract"].browse(self.env.context["active_id"])
        defaults["contract_id"] = contract.id
        defaults["payment_mode"] = self.env.ref(
            "somconnexio.payment_mode_inbound_sepa"
        ).id
        defaults["change_date"] = date.today()
        return defaults

    @api.depends("partner_id")
    def _compute_available_email_ids(self):
        if self.partner_id:
            self.available_email_ids = [
                (6, 0, self.partner_id.get_available_email_ids())
            ]

    @api.depends("partner_id")
    def _compute_available_banking_mandates(self):
        if self.partner_id:
            partner_mandates = self.env["account.banking.mandate"].search(
                [
                    ("partner_id", "=", self.partner_id.id),
                ]
            )
            self.available_banking_mandates = partner_mandates

    @api.depends("partner_id")
    def _compute_available_products(self):
        if not self.partner_id:
            return
        mbl_product_templates = self.env["product.template"].search(
            [
                ("categ_id", "=", self.env.ref("somconnexio.mobile_service").id),
            ]
        )
        self.available_products = self.env["product.product"].search(
            [
                ("product_tmpl_id", "in", mbl_product_templates.ids),
                ("active", "=", True),
                ("product_is_pack_exclusive", "=", False),
            ]
        )

    def button_change(self):
        self.ensure_one()

        changing_holder_contracts = self.contract_id

        if self.change_all_contracts_from_pack == "yes":
            changing_holder_contracts = self.contract_id.contracts_in_pack

        fiber_contract = changing_holder_contracts.filtered("is_fiber")
        new_fiber_contract = None

        if fiber_contract:
            crm_lead_line = self._create_new_crm_lead_line(fiber_contract)
            new_fiber_contract = self._create_new_contract(
                fiber_contract, crm_lead_line
            )
            self._terminate_contract(
                fiber_contract,
                new_fiber_contract,
                is_pack=self.change_all_contracts_from_pack == "yes",
            )

        mobile_contracts = changing_holder_contracts.filtered("is_mobile")

        for contract in mobile_contracts:
            crm_lead_line = self._create_new_crm_lead_line(contract)
            new_contract = self._create_new_contract(contract, crm_lead_line)
            self._terminate_contract(
                contract,
                new_contract,
                is_pack=self.change_all_contracts_from_pack == "yes",
            )
            if new_fiber_contract:
                new_contract.write({"parent_pack_contract_id": new_fiber_contract.id})

        return True

    def _get_or_create_service_partner_id(self, contract):
        service_partner = self.env["res.partner"].search(
            [
                ("parent_id", "=", self.partner_id.id),
                ("type", "=", "service"),
                ("street", "ilike", contract.service_partner_id.street),
            ],
            limit=1,
        )

        if not service_partner:
            service_partner = self.env["res.partner"].create(
                {
                    "parent_id": self.partner_id.id,
                    "name": "New partner service",
                    "type": "service",
                    "street": contract.service_partner_id.street,
                    "street2": contract.service_partner_id.street2,
                    "city": contract.service_partner_id.city,
                    "zip": contract.service_partner_id.zip,
                    "state_id": contract.service_partner_id.state_id.id,
                    "country_id": contract.service_partner_id.country_id.id,
                }
            )

        return service_partner

    def _create_new_crm_lead_line(self, contract):
        product = (
            self.product_id.categ_id == contract.current_tariff_product.categ_id
            and self.product_id
        ) or contract.current_tariff_product

        isp_info_params = {
            "type": "holder_change",
            "phone_number": contract.phone_number,
        }
        line_params = {
            "name": product.custom_name,
            "product_id": product.id,
            "product_tmpl_id": product.product_tmpl_id.id,
            "category_id": product.product_tmpl_id.categ_id.id,
            "iban": self.banking_mandate_id.partner_bank_id.sanitized_acc_number,
        }
        if contract.is_broadband:
            broadband_isp_info = self.env["broadband.isp.info"].create(isp_info_params)
            line_params.update({"broadband_isp_info": broadband_isp_info.id})
        else:
            mobile_isp_info = self.env["mobile.isp.info"].create(isp_info_params)
            line_params.update({"mobile_isp_info": mobile_isp_info.id})

        crm_lead_line = self.env["crm.lead.line"].create(line_params)

        self.env["crm.lead"].create(
            {
                "name": _("Change Holder process"),
                "description": self.notes,
                "partner_id": self.partner_id.id,
                "lead_line_ids": [(6, 0, [crm_lead_line.id])],
                "stage_id": self.env.ref("crm.stage_lead4").id,
            }
        )
        return crm_lead_line

    def _create_new_contract(self, contract, crm_lead_line):
        service_partner = self._get_or_create_service_partner_id(contract)
        new_contract_params = {
            "partner_id": self.partner_id.id,
            "service_partner_id": service_partner.id,
            "payment_mode_id": self.payment_mode.id,
            "mandate_id": self.banking_mandate_id.id,
            "email_ids": [(6, 0, [email.id for email in self.email_ids])],
            "journal_id": contract.journal_id.id,
            "service_technology_id": contract.service_technology_id.id,
            "service_supplier_id": contract.service_supplier_id.id,
            "contract_line_ids": [
                (0, 0, self._prepare_create_line(line))
                for line in contract.contract_line_ids
                if (
                    (not line.date_end or line.date_end > date.today())
                    and line.product_id.categ_id
                    not in (
                        self.env.ref("somconnexio.mobile_oneshot_service"),
                        self.env.ref("somconnexio.broadband_oneshot_service"),
                        self.env.ref("somconnexio.broadband_oneshot_adsl_service"),
                    )
                )
            ],
            "crm_lead_line_id": crm_lead_line.id,
        }

        # TODO: This code is duplicated in ContractServiceProcess
        if contract.mobile_contract_service_info_id:
            name_contract_info = "mobile_contract_service_info_id"
        elif contract.adsl_service_contract_info_id:
            name_contract_info = "adsl_service_contract_info_id"
        elif contract.vodafone_fiber_service_contract_info_id:
            name_contract_info = "vodafone_fiber_service_contract_info_id"
        elif contract.mm_fiber_service_contract_info_id:
            name_contract_info = "mm_fiber_service_contract_info_id"
        elif contract.router_4G_service_contract_info_id:
            name_contract_info = "router_4G_service_contract_info_id"
        contract_info = getattr(contract, name_contract_info)
        new_contract_params["name"] = contract_info.phone_number
        new_contract_params[name_contract_info] = contract_info.copy().id

        return self.env["contract.contract"].create(new_contract_params)

    def _terminate_contract(self, contract, new_contract, is_pack=False):
        terminate_reason = (
            self.env.ref("somconnexio.reason_holder_change_pack")
            if is_pack
            else self.env.ref("somconnexio.reason_holder_change")
        )
        contract.terminate_contract(
            terminate_reason,
            "New contract created with ID: {}\nNotes: {}".format(
                new_contract.id, self.notes or ""
            ),
            self.change_date,
            self.env.ref("somconnexio.user_reason_other"),
        )

        message = _(
            """
            Holder change wizard
            New contract created with ID: {}
            Notes: {}
            """
        )
        contract.message_post(message.format(new_contract.id, self.notes or ""))

    def _prepare_create_line(self, line):
        # If new product defined (mobile in pack, only contract changed)
        # use this new tariff
        product = (
            self.product_id.categ_id == line.product_id.categ_id and self.product_id
        ) or line.product_id

        return {
            "name": product.name,
            "product_id": product.id,
            "date_start": self.change_date + timedelta(days=1),
        }

    @api.onchange("partner_id")
    def check_partner_id_change(self):
        self.banking_mandate_id = False
        self.email_ids = False
