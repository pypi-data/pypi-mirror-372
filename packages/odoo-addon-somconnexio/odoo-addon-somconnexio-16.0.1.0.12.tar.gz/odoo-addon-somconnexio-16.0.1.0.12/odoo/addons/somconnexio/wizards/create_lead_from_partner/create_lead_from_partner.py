from odoo import models, fields, api, _
from odoo.exceptions import MissingError


class CreateLeadFromPartnerWizard(models.TransientModel):
    _name = "partner.create.lead.wizard"

    partner_id = fields.Many2one("res.partner")
    title = fields.Char(
        readonly=True,
        translate=True,
    )
    opportunity = fields.Char(required=True)
    bank_id = fields.Many2one(
        "res.partner.bank",
        string="Bank Account",
        required=True,
    )
    product_categ_id = fields.Many2one(
        "product.category",
        string="Service Technology",
        required=True,
    )
    available_product_categories = fields.Many2many(
        "product.category",
        compute="_compute_available_product_categories",
    )
    has_mobile_pack_offer_text = fields.Selection(
        [("yes", _("Yes")), ("no", "No")],
        string="Is mobile pack offer available?",
        readonly=True,
    )
    available_products = fields.Many2many(
        "product.product",
        compute="_compute_available_products",
        default=False,
    )
    available_email_ids = fields.Many2many(
        "res.partner",
        compute="_compute_available_email_ids",
    )
    email_id = fields.Many2one(
        "res.partner",
        string="Email",
        required=True,
    )
    phone_contact = fields.Char(
        string="Contact phone number",
        required=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Requested product",
        required=True,
    )
    icc = fields.Char(string="ICC")
    type = fields.Selection(
        [("portability", "Portability"), ("new", "New")],
        string="Type",
    )
    previous_contract_type = fields.Selection(
        [("contract", "Contract"), ("prepaid", "Prepaid")],
        string="Previous Contract Type",
    )
    team_id = fields.Many2one(
        "crm.team",
        string="Sales Team",
        required=True,
    )
    phone_number = fields.Char(string="Phone Number")
    donor_icc = fields.Char(string="ICC Donor")
    previous_mobile_provider = fields.Many2one(
        "previous.provider", string="Previous Provider"
    )
    previous_BA_provider = fields.Many2one(
        "previous.provider", string="Previous Provider"
    )
    previous_BA_service = fields.Selection(
        selection=[("fiber", "Fiber"), ("adsl", "ADSL"), ("4G", "4G")],
        string="Previous Service",
    )
    previous_owner_vat_number = fields.Char(string="Previous Owner VatNumber")
    previous_owner_first_name = fields.Char(string="Previous Owner First Name")
    previous_owner_name = fields.Char(string="Previous Owner Name")
    keep_landline = fields.Boolean(
        string="Keep Phone Number",
        default=False,
    )
    landline = fields.Char(string="Landline Phone Number")
    without_fix = fields.Boolean(related="product_id.without_fix")
    is_provisioning_required = fields.Boolean(
        compute="_compute_is_provisioning_required",
        string="Is Provisioning Required",
    )

    # Addresses
    is_service_address_required = fields.Boolean(
        compute="_compute_is_service_address_required",
        string="Service Address Required",
        default=False,
    )
    is_delivery_address_required = fields.Boolean(
        compute="_compute_is_delivery_address_required",
        string="Delivery Address Required",
        default=False,
    )
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
    invoice_street = fields.Char(string="Invoice Street")
    invoice_zip_code = fields.Char(string="Invoice ZIP")
    invoice_city = fields.Char(string="Invoice City")
    invoice_state_id = fields.Many2one("res.country.state", string="Invoice State")
    invoice_country_id = fields.Many2one("res.country", string="Invoice Country")
    service_street = fields.Char(string="Service Street")
    service_zip_code = fields.Char(string="Service ZIP")
    service_city = fields.Char(string="Service City")
    service_state_id = fields.Many2one("res.country.state", string="Service State")
    service_country_id = fields.Many2one("res.country", string="Service Country")
    fiber_contract_to_link = fields.Many2one("contract.contract")

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults["partner_id"] = self.env.context["active_id"]
        spain_country_id = self.env["res.country"].search([("code", "=", "ES")]).id
        defaults["service_country_id"] = spain_country_id
        defaults["delivery_country_id"] = spain_country_id
        defaults["invoice_country_id"] = spain_country_id
        defaults["title"] = _("Manual CRMLead creation from partner")
        partner_id = self.env["res.partner"].browse(defaults["partner_id"])
        defaults["phone_contact"] = partner_id.mobile or partner_id.phone
        defaults["fiber_contract_to_link"] = self._default_fiber_contract_to_link(
            partner_id.ref
        )
        defaults["has_mobile_pack_offer_text"] = (
            "yes" if defaults["fiber_contract_to_link"] else "no"
        )
        defaults["team_id"] = self.env.ref("somconnexio.residential").id
        return defaults

    def _default_fiber_contract_to_link(self, partner_ref):
        service = self.env["fiber.contract.to.pack.service"]
        try:
            fiber_contracts = service.create(partner_ref=partner_ref)
        except MissingError:
            return False
        else:
            return fiber_contracts[0].id

    def _get_available_categories(self):
        return (
            self.env["service.technology"]
            .search([])
            .mapped("service_product_category_id")
        )

    @api.depends("partner_id")
    def _compute_available_email_ids(self):
        if self.partner_id:
            self.available_email_ids = [
                (6, 0, self.partner_id.get_available_email_ids())
            ]

    @api.depends("partner_id")
    def _compute_available_product_categories(self):
        if not self.partner_id:
            return
        category_ids = self._get_available_categories()
        self.available_product_categories = [(6, 0, [c.id for c in category_ids])]

    @api.depends("product_categ_id")
    def _compute_is_provisioning_required(self):
        if not self.product_categ_id:
            self.is_provisioning_required = False
            return

        service_technology = self.env["service.technology"].search(
            [("service_product_category_id", "=", self.product_categ_id.id)],
            limit=1,
        )
        self.is_provisioning_required = (
            service_technology.external_provisioning_required
        )

    @api.depends("product_categ_id")
    def _compute_is_service_address_required(self):
        """Compute if service address is required based on product category."""
        if not self.product_categ_id:
            self.is_service_address_required = False
            return

        broadband_categories = self.env["product.category"].search(
            [("id", "child_of", self.env.ref("somconnexio.broadband_service").id)]
        )
        self.is_service_address_required = self.product_categ_id in broadband_categories

    @api.depends("product_categ_id", "icc")
    def _compute_is_delivery_address_required(self):
        """Compute if delivery address is required based on product category."""
        if not self.product_categ_id:
            self.is_delivery_address_required = False
            return

        self.is_delivery_address_required = (
            self.product_categ_id == self.env.ref("somconnexio.mobile_service")
            and not self.icc
        )

    @api.depends("product_categ_id", "team_id")
    def _compute_available_products(self):
        if not self.product_categ_id:
            self.available_products = False
            return

        available_product_templates = self._get_available_product_templates()

        # Filter out la Borda products for fiber services
        if self.product_categ_id == self.env.ref("somconnexio.broadband_fiber_service"):
            available_product_templates = available_product_templates.filtered(
                lambda p: "borda" not in p.name.lower()
            )

        product_search_domain = [
            ("product_tmpl_id", "in", available_product_templates.ids),
        ]

        attr_to_exclude = self.env["product.attribute.value"]
        attr_to_include = self.env["product.attribute.value"]
        if self.has_mobile_pack_offer_text == "no":
            attr_to_exclude |= self.env.ref("somconnexio.IsInPack")
        if self.team_id == self.env.ref("somconnexio.business"):
            attr_to_include |= self.env.ref("somconnexio.CompanyExclusive")
        else:
            attr_to_exclude |= self.env.ref("somconnexio.CompanyExclusive")

        if attr_to_exclude:
            product_search_domain.append(
                (
                    "product_template_attribute_value_ids.product_attribute_value_id",
                    "not in",
                    attr_to_exclude.ids,
                )
            )
        if attr_to_include:
            product_search_domain.append(
                (
                    "product_template_attribute_value_ids.product_attribute_value_id",
                    "in",
                    attr_to_include.ids,
                )
            )
        self.available_products = self.env["product.product"].search(
            product_search_domain
        )

    def _get_available_product_templates(self):
        """Get available product templates based on the selected product category."""
        if not self.product_categ_id:
            return self.env["product.template"]

        product_templates = self.env["product.template"].search(
            [("categ_id", "=", self.product_categ_id.id)]
        )
        return product_templates

    def create_lead(self):
        self.ensure_one()

        if not (self.partner_id.phone or self.partner_id.mobile):
            self.partner_id.write({"phone": self.phone_contact})

        line_params = {
            "name": self.product_id.name,
            "product_id": self.product_id.id,
            "product_tmpl_id": self.product_id.product_tmpl_id.id,
            "category_id": self.product_id.product_tmpl_id.categ_id.id,
            "iban": self.bank_id.sanitized_acc_number,
        }

        if self.is_provisioning_required:
            isp_info_model_name, isp_info_res_id = self._create_isp_info_params()
            isp_info_param = isp_info_model_name.replace(".", "_")

            line_params.update(
                {
                    isp_info_param: isp_info_res_id.id,
                }
            )

        crm = self.env["crm.lead"].create(
            {
                "name": self.opportunity,
                "description": "",
                "partner_id": self.partner_id.id,
                "email_from": self.email_id.email,
                "phone": self.phone_contact,
                "team_id": self.team_id.id,
                "lead_line_ids": [(0, _, line_params)],
            }
        )

        view_ref = "somconnexio.crm_case_form_view_pack"
        action = self.env.ref("somconnexio.act_crm_lead_pack").read()[0]

        action.update(
            {
                "target": "current",
                "xml_id": view_ref,
                "views": [[self.env.ref(view_ref).id, "form"]],
                "res_id": crm.id,
            }
        )

        return action

    def _create_isp_info_params(self):
        isp_info_model_name = None
        isp_info_args = {
            "type": self.type,
            "delivery_street": self.delivery_street,
            "delivery_zip_code": self.delivery_zip_code,
            "delivery_city": self.delivery_city,
            "delivery_state_id": self.delivery_state_id.id,
            "delivery_country_id": self.delivery_country_id.id,
            "invoice_street": self.invoice_street,
            "invoice_zip_code": self.invoice_zip_code,
            "invoice_city": self.invoice_city,
            "invoice_state_id": self.invoice_state_id.id,
            "invoice_country_id": self.invoice_country_id.id,
            "previous_owner_vat_number": self.previous_owner_vat_number,
            "previous_owner_name": self.previous_owner_name,
            "previous_owner_first_name": self.previous_owner_first_name,
        }

        if self.product_categ_id == self.env.ref("somconnexio.mobile_service"):
            isp_info_model_name = "mobile.isp.info"
            isp_info_args.update(
                {
                    "icc": self.icc,
                    "icc_donor": self.donor_icc,
                    "phone_number": self.phone_number,
                    "previous_contract_type": self.previous_contract_type,
                    "previous_provider": self.previous_mobile_provider.id,
                    "linked_fiber_contract_id": (
                        self.fiber_contract_to_link.id
                        if self.product_id.product_is_pack_exclusive
                        else False
                    ),
                }
            )
        else:
            isp_info_model_name = "broadband.isp.info"
            previous_phone_number = False
            if self.product_id.without_fix:
                phone_number = "-"
                if self.type == "portability":
                    previous_phone_number = self.landline
            else:
                phone_number = self.landline
            isp_info_args.update(
                {
                    "keep_phone_number": self.keep_landline,
                    "phone_number": phone_number,
                    "previous_phone_number": previous_phone_number,
                    "previous_provider": self.previous_BA_provider.id,
                    "previous_service": self.previous_BA_service,
                    "service_street": self.service_street,
                    "service_zip_code": self.service_zip_code,
                    "service_city": self.service_city,
                    "service_state_id": self.service_state_id.id,
                    "service_country_id": self.service_country_id.id,
                }
            )

        isp_info_res_id = self.env[isp_info_model_name].create(isp_info_args)

        return isp_info_model_name, isp_info_res_id
