import logging

from odoo import _
from odoo.addons.component.core import Component

from . import schemas

_logger = logging.getLogger(__name__)


class OneShotCatalog(Component):
    _inherit = "base.rest.service"
    _name = "one_shot_catalog.service"
    _usage = "one-shot-catalog"
    _collection = "sc.api.key.services"
    _description = """
        Product catalog service to expose all the SomConnexió one shot products
        and their prices and other attributes.
        Filtering by product_code is enabled to get the list of specific one shot
        available for a product.
    """

    def search(self, code="21IVA", product_code=None):
        _logger.info("Searching product one shot catalog...")

        one_shots = self._get_filter_one_shots(product_code)
        domain = [("code", "=", code)]
        pricelists = self.env["product.pricelist"].search(domain)

        return {
            "pricelists": [
                self._build_response_from_pricelist(pricelist, one_shots)
                for pricelist in pricelists
            ]
        }

    def _get_filter_one_shots(self, product_code):
        if not product_code:
            return []
        product = self.env["product.product"].search(
            [("default_code", "=", product_code)]
        )
        domain = [
            ("public", "=", True),
            ("has_sharing_data_bond", "=", product.has_sharing_data_bond),
            ("categ_id.parent_id", "!=", None),
            (
                "categ_id.parent_id",
                "in",
                [
                    id
                    for id in [product.categ_id.id, product.categ_id.parent_id.id]
                    if id
                ],
            ),
            ("categ_id.name", "ilike", "%one%shot%"),
        ]
        return self.env["product.product"].search(domain)

    def _build_response_from_pricelist(self, pricelist, one_shots):
        pricelist_data = {
            "code": pricelist.code,
            "one_shots": [
                self._extract_product_info(p, pricelist.id) for p in one_shots
            ],
        }
        return pricelist_data

    def _extract_product_info(self, product, pricelist_id):
        product.ensure_one()
        pricelist = self.env["product.pricelist"].browse(pricelist_id)
        return {
            "code": product.default_code,
            "name": _(product.showed_name),
            "price": pricelist._compute_price_rule(product, 1)[product.id][0],
            "minutes": self._get_minutes(product),
            "data": self._get_data(product),
        }

    def _get_minutes(self, product):
        min = product.without_lang().get_catalog_name("Min")
        return 99999 if min == "UNL" else int(min)

    def _get_data(self, product):
        data = product.without_lang().get_catalog_name("Data")
        return int(data)

    def _validator_search(self):
        return schemas.S_ONE_SHOT_CATALOG_REQUEST_SEARCH

    def _validator_return_search(self):
        return schemas.S_ONE_SHOT_CATALOG_RETURN_SEARCH
