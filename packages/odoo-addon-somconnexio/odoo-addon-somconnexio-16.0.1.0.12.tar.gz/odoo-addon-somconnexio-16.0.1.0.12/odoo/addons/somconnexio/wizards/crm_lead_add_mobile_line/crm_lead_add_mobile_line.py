from odoo import api, fields, models


class CRMLeadAddMobileLine(models.TransientModel):
    _name = "crm.lead.add.mobile.line.wizard"
    crm_lead_id = fields.Many2one("crm.lead")

    @api.model
    def _product_id_domain(self):
        return [("categ_id", "=", self.env.ref("somconnexio.mobile_service").id)]

    product_id = fields.Many2one(
        "product.product",
        string="Requested product",
        required=True,
        domain=_product_id_domain,
    )
    partner_id = fields.Many2one("res.partner")
    bank_id = fields.Many2one(
        "res.partner.bank",
        string="Bank Account",
        required=True,
    )
    icc = fields.Char(string="ICC")
    type = fields.Selection(
        [("portability", "Portability"), ("new", "New")],
        string="Type",
        required=True,
    )
    previous_contract_type = fields.Selection(
        [("contract", "Contract"), ("prepaid", "Prepaid")],
        string="Previous Contract Type",
    )
    phone_number = fields.Char(string="Phone Number")
    donor_icc = fields.Char(string="ICC Donor")
    previous_mobile_provider = fields.Many2one(
        "previous.provider", string="Previous Provider"
    )
    previous_owner_vat_number = fields.Char(string="Previous Owner VatNumber")
    previous_owner_first_name = fields.Char(string="Previous Owner First Name")
    previous_owner_name = fields.Char(string="Previous Owner Name")
    keep_landline = fields.Boolean(
        string="Keep Phone Number",
        default=False,
    )
    # Addresses
    delivery_street = fields.Char(string="Delivery Street")
    delivery_zip_code = fields.Char(string="Delivery ZIP")
    delivery_city = fields.Char(string="Delivery City")
    delivery_state_id = fields.Many2one(
        "res.country.state",
        string="Delivery State",
    )
    delivery_country_id = fields.Many2one(
        "res.country",
        string="Delivery Country",
    )

    def button_create(self):
        self.ensure_one()
        mobile_isp_info = self.env["mobile.isp.info"].create(
            {
                "type": self.type,
                "delivery_street": self.delivery_street,
                "delivery_zip_code": self.delivery_zip_code,
                "delivery_city": self.delivery_city,
                "delivery_state_id": self.delivery_state_id.id,
                "delivery_country_id": self.delivery_country_id.id,
                "previous_owner_vat_number": self.previous_owner_vat_number,
                "previous_owner_name": self.previous_owner_name,
                "previous_owner_first_name": self.previous_owner_first_name,
                "icc": self.icc,
                "icc_donor": self.donor_icc,
                "phone_number": self.phone_number,
                "previous_contract_type": self.previous_contract_type,
                "previous_provider": self.previous_mobile_provider.id,
            }
        )
        lead_line = self.env["crm.lead.line"].create(
            {
                "name": self.product_id.name,
                "product_id": self.product_id.id,
                "product_tmpl_id": self.product_id.product_tmpl_id.id,
                "category_id": self.product_id.product_tmpl_id.categ_id.id,
                "mobile_isp_info": mobile_isp_info.id,
                "iban": self.bank_id.sanitized_acc_number,
            }
        )
        self.crm_lead_id.write({"lead_line_ids": [(4, lead_line.id, 0)]})
        return True

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        spain_country_id = self.env["res.country"].search([("code", "=", "ES")]).id
        defaults["delivery_country_id"] = spain_country_id
        crm_lead_id = self.env["crm.lead"].browse(self.env.context["active_id"])
        defaults["crm_lead_id"] = crm_lead_id.id
        defaults["partner_id"] = crm_lead_id.partner_id.id

        if crm_lead_id.has_mobile_lead_lines:
            line = crm_lead_id.mobile_lead_line_ids[0]
            defaults["delivery_street"] = line.mobile_isp_info.delivery_street
            defaults["delivery_zip_code"] = line.mobile_isp_info.delivery_zip_code
            defaults["delivery_city"] = line.mobile_isp_info.delivery_city
            defaults["delivery_state_id"] = line.mobile_isp_info.delivery_state_id.id
        return defaults
