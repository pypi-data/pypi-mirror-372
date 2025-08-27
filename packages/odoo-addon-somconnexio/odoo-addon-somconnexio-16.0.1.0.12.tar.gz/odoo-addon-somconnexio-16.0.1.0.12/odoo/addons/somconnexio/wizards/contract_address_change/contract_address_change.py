from odoo import api, fields, models, _


class ContractAddressChangeWizard(models.TransientModel):
    _name = "contract.address.change.wizard"

    contract_id = fields.Many2one("contract.contract")
    partner_id = fields.Many2one("res.partner", related="contract_id.partner_id")

    partner_bank_id = fields.Many2one(
        "res.partner.bank", string="Partner Bank", required=True
    )
    service_street = fields.Char(string="Service Street", required=True)
    service_street2 = fields.Char(string="Service Street 2")
    service_zip_code = fields.Char(string="Service ZIP", required=True)
    service_city = fields.Char(string="Service City", required=True)
    service_state_id = fields.Many2one(
        "res.country.state", string="Service State", required=True
    )
    service_country_id = fields.Many2one(
        "res.country", string="Service Country", required=True
    )
    previous_tariff_contract_line = fields.Many2one(
        "contract.line",
        related="contract_id.current_tariff_contract_line",
    )
    previous_product_id = fields.Many2one(
        "product.product",
        "Previous Product",
        related="previous_tariff_contract_line.product_id",
    )
    service_supplier_id = fields.Many2one(
        "service.supplier",
        "Service Supplier",
        related="contract_id.service_supplier_id",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Requested product",
        required=True,
    )
    can_keep_landline = fields.Boolean(
        compute="_compute_can_keep_landline",
        default=False,
    )
    keep_phone_number = fields.Boolean(
        string="Keep Phone Number",
    )
    new_product_category_id = fields.Many2one(
        "product.category",
        related="product_id.product_tmpl_id.categ_id",
    )
    notes = fields.Text(
        string="Notes",
    )
    previous_contract_phone = fields.Char(
        related="contract_id.phone_number",
    )
    previous_contract_address = fields.Char(
        compute="_compute_previous_contract_address",
    )
    previous_contract_pon = fields.Char(
        compute="_compute_previous_contract_pon",
    )
    previous_contract_fiber_speed = fields.Char(
        compute="_compute_previous_contract_fiber_speed",
    )

    def _get_broadband_isp_info_params(self):
        return {
            "service_street": self.service_street,
            "service_street2": self.service_street2,
            "service_city": self.service_city,
            "service_zip_code": self.service_zip_code,
            "service_state_id": self.service_state_id.id,
            "service_country_id": self.service_country_id.id,
            "type": "location_change",
            "previous_service": self._previous_service(),
            "service_supplier_id": self.service_supplier_id.id,
            "previous_owner_vat_number": self.partner_id.vat,
            "previous_owner_first_name": self.partner_id.firstname,
            "previous_owner_name": self.partner_id.lastname,
            "previous_contract_address": self.previous_contract_address,
            "phone_number": self.previous_contract_phone,
            "previous_contract_phone": self.previous_contract_phone,
            "previous_contract_pon": self.previous_contract_pon,
            "previous_contract_fiber_speed": self.previous_contract_fiber_speed,
            "mobile_pack_contracts": [
                (
                    6,
                    0,
                    self.contract_id.children_pack_contract_ids.mapped("id"),
                )
            ],
            "previous_provider": self.env.ref("somconnexio.previousprovider52").id,
            "keep_phone_number": self.keep_phone_number,
        }

    def _get_crm_lead_line_params(self, broadband_isp_info):
        return {
            "name": self.product_id.name,
            "product_id": self.product_id.id,
            "product_tmpl_id": self.product_id.product_tmpl_id.id,
            "category_id": self.product_id.product_tmpl_id.categ_id.id,
            "broadband_isp_info": broadband_isp_info.id,
            "iban": self.partner_bank_id.sanitized_acc_number,
        }

    def _get_crm_lead_params(self, crm_lead_line):
        return {
            "name": _("Change Address process"),
            "description": self.notes,
            "partner_id": self.partner_id.id,
            "lead_line_ids": [(6, 0, [crm_lead_line.id])],
        }

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults["service_country_id"] = (
            self.env["res.country"].search([("code", "=", "ES")]).id
        )
        contract = self.env["contract.contract"].browse(self.env.context["active_id"])
        defaults["contract_id"] = contract.id
        defaults["partner_bank_id"] = contract.mandate_id.partner_bank_id.id
        return defaults

    def _previous_service(self):
        service_technology = {
            self.env.ref("somconnexio.broadband_adsl_service").id: "adsl",
            self.env.ref("somconnexio.broadband_fiber_service").id: "fiber",
        }
        return service_technology.get(
            self.previous_product_id.product_tmpl_id.categ_id.id
        )

    @api.depends("contract_id")
    def _compute_previous_contract_address(self):
        self.previous_contract_address = "{}, {} - {} ({})".format(
            self.contract_id.service_partner_id.full_street,
            self.contract_id.service_partner_id.city,
            self.contract_id.service_partner_id.zip,
            self.contract_id.service_partner_id.state_id.name,
        )

    @api.depends("contract_id")
    def _compute_previous_contract_pon(self):
        if self.contract_id.vodafone_fiber_service_contract_info_id:
            self.previous_contract_pon = (
                self.contract_id.vodafone_fiber_service_contract_info_id.vodafone_id
            )
        else:
            self.previous_contract_pon = ""

    @api.depends("contract_id")
    def _compute_previous_contract_fiber_speed(self):
        if (
            self.contract_id.vodafone_fiber_service_contract_info_id
            or self.contract_id.mm_fiber_service_contract_info_id
        ):
            # All fiber products have a single Bandwith attribute value, their velocity
            # (100Mb/300Mb/600Mb/1Gb)

            previous_contract_product = (
                self.contract_id.current_tariff_contract_line.product_id
            )
            ptav = (
                previous_contract_product.product_template_attribute_value_ids.filtered(
                    lambda ptav: ptav.product_tmpl_id
                    == self.env.ref("somconnexio.Fibra_product_template")
                    and ptav.attribute_id == self.env.ref("somconnexio.Bandwidth")
                )
            )
            self.previous_contract_fiber_speed = (
                ptav.product_attribute_value_id.name if ptav else ""
            )

        elif self.contract_id.xoln_fiber_service_contract_info_id:
            # Greta fiber contracts have 600Mb
            self.previous_contract_fiber_speed = "600Mb"
        else:
            self.previous_contract_fiber_speed = ""

    @api.depends("previous_product_id", "product_id")
    def _compute_can_keep_landline(self):
        if not self.product_id:
            return

        self.can_keep_landline = not (
            self.previous_product_id.without_fix or self.product_id.without_fix
        )

    def button_change(self):
        self.ensure_one()
        broadband_isp_info_params = self._get_broadband_isp_info_params()
        broadband_isp_info = self.env["broadband.isp.info"].create(
            broadband_isp_info_params
        )
        line_params = self._get_crm_lead_line_params(broadband_isp_info)
        crm_lead_line = self.env["crm.lead.line"].create(line_params)
        lead_params = self._get_crm_lead_params(crm_lead_line)
        self.env["crm.lead"].create(lead_params)

        action = self.env.ref("somconnexio.act_crm_lead_pack").read()[0]

        action.update(
            {
                "target": "current",
                "xml_id": "somconnexio.crm_case_form_view_pack",
                "views": [
                    [self.env.ref("somconnexio.crm_case_form_view_pack").id, "form"]
                ],
                "res_id": crm_lead_line.lead_id.id,
            }
        )

        return action
