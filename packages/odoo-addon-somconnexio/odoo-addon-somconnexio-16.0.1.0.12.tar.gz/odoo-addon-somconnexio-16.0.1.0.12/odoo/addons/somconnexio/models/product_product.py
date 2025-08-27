from odoo import api, fields, models, _


class Product(models.Model):
    _inherit = ["product.product"]
    _name = "product.product"

    _sql_constraints = [
        (
            "default_code_uniq",
            "unique (default_code)",
            "The product code must be unique !",
        ),
    ]

    public = fields.Boolean(
        string="Public",
        help="This field selects if the products that we expose in the catalog API.",
        default=False,
    )

    custom_name = fields.Char(
        string="Custom name",
        translate=True,
    )

    showed_name = fields.Char(
        string="Name",
        compute="_compute_showed_name",
        inverse="_inverse_showed_name",
        translate=True,
        store=True,
    )

    without_fix = fields.Boolean("Product without fix number", default=False)
    contract_as_new_service = fields.Boolean("Contract as new service", default=True)

    has_custom_products_to_change_tariff = fields.Boolean(
        help="""
        This flag allows select a list of products to allow change tariff from
        this product.
        If this flag is not selected, all the products from the same category
        will be available in change tariff process.
        """
    )

    products_available_change_tariff = fields.Many2many(
        "product.product",
        "product_product_change_tariff_rel",
        "main_product_id",
        "product_id",
        string="Available Products to Change Tariff",
    )

    product_is_pack_exclusive = fields.Boolean(
        compute="_compute_is_pack_exclusive",
        default=False,
    )

    has_sharing_data_bond = fields.Boolean(
        string="Is sharing mobile data?", default=False
    )

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        if name:
            if args:
                new_args = [
                    "&",
                    "|",
                    ("showed_name", operator, name),
                    ("default_code", operator, name),
                ] + args
            else:
                new_args = [
                    "|",
                    ("showed_name", operator, name),
                    ("default_code", operator, name),
                ]
            product_ids = self.env["product.product"]._search(
                args=new_args,
                limit=limit,
                access_rights_uid=name_get_uid,
            )
            return product_ids
        else:
            return super()._name_search(
                name=name,
                args=args,
                operator=operator,
                limit=limit,
                name_get_uid=name_get_uid,
            )

    @api.depends("product_template_attribute_value_ids")
    def _compute_is_pack_exclusive(self):
        pack_attr = self.env.ref("somconnexio.IsInPack", raise_if_not_found=False)
        if not pack_attr:
            return

        for product in self:
            product.product_is_pack_exclusive = False
            product.product_is_pack_exclusive = bool(
                pack_attr
                in product.product_template_attribute_value_ids.mapped(
                    "product_attribute_value_id"
                )
            )

    # TAKE IN MIND: We can overwrite this method from product_product for now,
    # but in the future we might need some additional features/conditions from
    # the original one:
    # https://github.com/odoo/odoo/blob/12.0/addons/product/models/product.py#L424
    def name_get(self):
        data = []
        for product in self:
            data.append((product.id, product.showed_name))
        return data

    @api.depends("custom_name")
    def _compute_showed_name(self):
        for product in self:
            product.showed_name = product.custom_name or product.showed_name or ""

    def _inverse_showed_name(self):
        for product in self:
            product.custom_name = product.showed_name

    def get_catalog_name(self, attribute_name):
        catalog_name = False
        for (
            product_template_attribute_value
        ) in self.product_template_attribute_value_ids:
            if product_template_attribute_value.attribute_id.name == attribute_name:
                catalog_name = (
                    product_template_attribute_value.product_attribute_value_id.catalog_name  # noqa
                )
        return catalog_name

    def without_lang(self):
        ctx = self.env.context.copy()
        if "lang" in ctx:
            del ctx["lang"]
        return self.with_context(ctx)

    def write(self, vals):
        for product in self:
            for key, value in vals.items():
                msg = _("Field '{}' edited from '{}' to '{}'")
                product.message_post(msg.format(key, getattr(product, key), value))
        super().write(vals)
        return True

    def get_offer(self):
        """
        Return the same product but the one with offer,
        only for mobiles products.
        Ex. If we execute this method for Unilimited 20GB
        it return Unilimited 20GB Pack
        """

        if self.product_tmpl_id.categ_id != self.env.ref("somconnexio.mobile_service"):
            return
        if self.has_sharing_data_bond or self.env.ref(
            "somconnexio.CompanyExclusive"
        ) in self.product_template_attribute_value_ids.mapped(
            "product_attribute_value_id"
        ):
            # TODO -> review, companies could have offers
            # Company exclusive and sharing data tariff
            # products are already an offer
            return

        attr_to_exclude = (
            self.env.ref("somconnexio.IsNotInPack")
            | self.env.ref("somconnexio.CompanyExclusive")
            | self.env.ref("somconnexio.Pack2Mobiles")
            | self.env.ref("somconnexio.Pack3Mobiles")
        )
        attr_to_include = self.env.ref("somconnexio.IsInPack")

        return self.get_variant_with_attributes(attr_to_exclude, attr_to_include)

    def get_variant_with_attributes(self, attr_to_exclude=False, attr_to_include=False):
        """
        Return the product that has the same attribute combination excluding
        some attributes and including others.
        """

        attr_combination = (
            self.product_template_attribute_value_ids.product_attribute_value_id
        )

        if attr_to_include:
            attr_combination += attr_to_include
        if attr_to_exclude:
            attr_combination -= attr_to_exclude

        product_template_attribute_values = self.env[
            "product.template.attribute.value"
        ].search(
            [
                ("product_attribute_value_id", "in", attr_combination.ids),
                ("product_tmpl_id", "=", self.product_tmpl_id.id),
            ]
        )

        return self.env["product.product"].browse(
            self.product_tmpl_id._get_variant_id_for_combination(
                product_template_attribute_values
            )
        )

    def get_technology(self):
        """
        Get the service technology corresponding to the product.
        If the product category does not have a service technology,
        it will search for the parent category's service technology.
        :return: The service technology record.
        """
        product_categ = self.product_tmpl_id.categ_id
        ServiceTechnology = self.env["service.technology"]
        domain = [("service_product_category_id", "=", product_categ.id)]
        service_technology = ServiceTechnology.search((domain), limit=1)

        if not service_technology.exists:
            domain = [("service_product_category_id", "=", product_categ.parent_id.id)]
        service_technology = ServiceTechnology.search((domain), limit=1)

        return service_technology
