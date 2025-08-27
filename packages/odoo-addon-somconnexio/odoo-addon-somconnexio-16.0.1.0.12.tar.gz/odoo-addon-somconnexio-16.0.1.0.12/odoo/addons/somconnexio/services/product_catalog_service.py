import logging

from odoo import _
from odoo.addons.component.core import Component

from . import schemas

_logger = logging.getLogger(__name__)


class ProductCatalog(Component):
    _inherit = "base.rest.service"
    _name = "product_catalog.service"
    _usage = "product-catalog"
    _collection = "sc.api.key.services"
    _description = """
        Product catalog service to expose all the SomConnexió service products
        and their prices and other attributes.
        Filtering by code is enabled to get a specific tax-related priceList.
        Filtering by service category is enabled to get products only
        Filtering by product code is enabled to get products available for a
        tariff change from selected product.
    """

    def search(self, code=None, categ=None, product_code=None, is_company=False):
        _logger.info("Searching product catalog...")

        CatalogService = self.env["catalog.service"]
        products_availables_from_product = (
            CatalogService.products_availables_from_product(product_code)
        )
        service_products = CatalogService.service_products(categ)
        sale_products = CatalogService.filter_sale_category_available_products(
            products=service_products, is_company=is_company
        )

        pack_products = CatalogService.pack_products()
        sale_pack_products = CatalogService.filter_sale_category_available_products(
            products=pack_products, is_company=is_company
        )
        domain = [("code", "=", code)] if code else [("code", "!=", False)]
        pricelists = self.env["product.pricelist"].search(domain)

        return {
            "pricelists": [
                self._build_response_from_pricelist(
                    pricelist,
                    sale_products,
                    sale_pack_products,
                    products_availables_from_product,
                )
                for pricelist in pricelists
            ]
        }

    def _build_response_from_pricelist(
        self, pricelist, products, pack_products, products_availables_from_product
    ):
        if products_availables_from_product:
            return {
                "code": pricelist.code,
                "products": [
                    self._extract_product_info(p, pricelist)
                    for p in products_availables_from_product
                ],
                "packs": [],
            }
        return {
            "code": pricelist.code,
            "products": [
                self._extract_product_info(p, pricelist)
                for p in products
                if p.contract_as_new_service
            ],
            "packs": [self._extract_pack_info(p, pricelist) for p in pack_products],
        }

    def _extract_product_info(self, product, pricelist):
        product.ensure_one()

        product_info = {
            "code": product.default_code,
            "name": _(product.showed_name),
            "price": pricelist._get_products_price(
                product,
                1,
            ).get(product.id, 0.0),
            "category": self._get_product_category(product),
            "minutes": None,
            "data": None,
            "bandwidth": None,
        }
        if product_info.get("category") == "mobile":
            product_info.update(
                {
                    "minutes": self._get_minutes_from_mobile_product(product),
                    "data": self._get_data_from_product(product),
                }
            )
        elif product_info.get("category") == "4G":
            product_info.update(
                {
                    "has_landline_phone": not bool(product.without_fix),
                    "data": self._get_data_from_product(product),
                }
            )
        else:
            product_info.update(
                {
                    "has_landline_phone": not bool(product.without_fix),
                    "bandwidth": self._get_bandwith_from_BA_product(product),
                }
            )

        offer_product = product.get_offer()
        if offer_product:
            product_info.update(
                {
                    "offer": {
                        "code": offer_product.default_code,
                        "price": pricelist._get_products_price(
                            offer_product,
                            1,
                        ).get(offer_product.id, 0.0),
                        "name": offer_product.showed_name,
                    }
                }
            )
        return product_info

    def _extract_pack_info(self, pack, pricelist):
        pack.ensure_one()
        ba_product = pack.pack_line_ids.mapped("product_id").filtered(
            lambda p: self._get_product_category(p) != "mobile"
        )
        mbl_pack_line_ids = pack.pack_line_ids.filtered(
            lambda l: self._get_product_category(l.product_id) == "mobile"
        )
        has_sharing_data_bond = mbl_pack_line_ids.mapped("product_id").filtered(
            "has_sharing_data_bond"
        )
        product_info = self._extract_product_info(pack, pricelist)

        product_info.update(
            {
                "category": (
                    "bonified_mobile"
                    if not has_sharing_data_bond
                    else "mobile_shared_data"
                ),
                "mobiles_in_pack": int(
                    sum(line.quantity for line in mbl_pack_line_ids)
                ),
                "fiber_bandwidth": self._get_bandwith_from_BA_product(ba_product),
                "has_land_line": not bool(ba_product.without_fix),
                "products": [
                    self._extract_product_info(line.product_id, pricelist)
                    for line in pack.pack_line_ids
                    for _ in range(int(line.quantity))
                ],
            }
        )
        # TODO: review this logic, the product_pack module use the price_lst
        # instead of the pricelist value
        price = 0.0
        for line in product_info["products"]:
            price += line["price"]
        product_info["price"] = price
        return product_info

    def _get_product_category(self, product):
        category = product.product_tmpl_id.categ_id
        if category == self.env.ref("somconnexio.mobile_service"):
            return "mobile"
        elif category == self.env.ref("somconnexio.broadband_fiber_service"):
            return "fiber"
        elif category == self.env.ref("somconnexio.broadband_adsl_service"):
            return "adsl"
        elif category == self.env.ref("somconnexio.broadband_4G_service"):
            return "4G"

    def _get_minutes_from_mobile_product(self, product):
        minutes = product.without_lang().get_catalog_name("Min")
        return 99999 if minutes == "UNL" else int(minutes)

    def _get_data_from_product(self, product):
        data = product.without_lang().get_catalog_name("Data")
        return int(data)

    def _get_bandwith_from_BA_product(self, product):
        bw = product.without_lang().get_catalog_name("Bandwidth")
        return int(bw)

    def _validator_search(self):
        return schemas.S_PRODUCT_CATALOG_REQUEST_SEARCH

    def _validator_return_search(self):
        return schemas.S_PRODUCT_CATALOG_RETURN_SEARCH
