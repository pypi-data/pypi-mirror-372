from odoo import models, api


class CatalogService(models.AbstractModel):
    _name = "catalog.service"

    @api.model
    def products_availables_from_product(self, product_code):
        if not product_code:
            return None
        product = self.env["product.product"].search(
            [("default_code", "=", product_code)]
        )
        if not product:
            return None
        return product.products_available_change_tariff

    @api.model
    def pack_products(self):
        pack_products = self.env["product.product"].search(
            [
                ("pack_ok", "=", True),
                ("public", "=", True),
            ]
        )
        return pack_products

    def service_products(self, service_category=None):
        mobile_categ_id = self.env.ref("somconnexio.mobile_service").id
        adsl_categ_id = self.env.ref("somconnexio.broadband_adsl_service").id
        fiber_categ_id = self.env.ref("somconnexio.broadband_fiber_service").id
        router_4G_categ_id = self.env.ref("somconnexio.broadband_4G_service").id

        category_id_list = []
        if not service_category:
            category_id_list.extend(
                [mobile_categ_id, adsl_categ_id, fiber_categ_id, router_4G_categ_id]
            )
        elif service_category == "mobile":
            category_id_list.append(mobile_categ_id)
        elif service_category == "adsl":
            category_id_list.append(adsl_categ_id)
        elif service_category == "fiber":
            category_id_list.append(fiber_categ_id)
        elif service_category == "4G":
            category_id_list.append(router_4G_categ_id)

        service_product_templates = self.env["product.template"].search(
            [
                ("categ_id", "in", category_id_list),
            ]
        )
        service_products = self._search_service_products_by_templates(
            service_product_templates
        )
        return service_products

    def filter_sale_category_available_products(self, products, is_company):
        if is_company == "true":
            attr_to_exclude = self.env.ref("somconnexio.ParticularExclusive")
        else:
            attr_to_exclude = self.env.ref("somconnexio.CompanyExclusive")

        available_products = products.filtered(
            lambda p: attr_to_exclude
            not in p.product_template_attribute_value_ids.product_attribute_value_id
        )
        return available_products

    def _search_service_products_by_templates(self, service_product_templates):
        service_products = self.env["product.product"].search(
            [
                (
                    "product_tmpl_id",
                    "in",
                    [tmpl.id for tmpl in service_product_templates],
                ),
                ("public", "=", True),
                ("contract_as_new_service", "=", True),
            ]
        )
        return service_products
