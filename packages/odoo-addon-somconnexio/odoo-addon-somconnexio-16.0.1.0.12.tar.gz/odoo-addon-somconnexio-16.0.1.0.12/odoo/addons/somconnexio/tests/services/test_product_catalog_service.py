import html
import json

from unittest.mock import patch

from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin
from odoo.tools import mute_logger


class TestProductCatalogController(BaseRestCaseAdmin):
    def setUp(self):
        super().setUp()
        self.url = "/api/product-catalog"
        self.code = "21IVA"
        self.params = {"code": self.code}
        self.demo_pricelist = self.browse_ref("somconnexio.pricelist_21_IVA")

        # Mobile product
        self.mbl_product = self.browse_ref("somconnexio.150Min1GB")
        self.expected_mobile_product_info = {
            "code": self.mbl_product.default_code,
            "name": self.mbl_product.showed_name,
            "price": self.demo_pricelist._get_products_price(
                self.mbl_product,
                1,
            ).get(self.mbl_product.id, 0.0),
            "category": "mobile",
            "minutes": 150,
            "data": 1024,
            "bandwidth": None,
        }

        # Fiber product
        self.fiber_product = self.browse_ref("somconnexio.Fibra600Mb")
        self.expected_fiber_product_info = {
            "code": self.fiber_product.default_code,
            "name": self.fiber_product.showed_name,
            "price": self.demo_pricelist._get_products_price(
                self.fiber_product,
                1,
            ).get(self.fiber_product.id, 0.0),
            "category": "fiber",
            "minutes": None,
            "data": None,
            "bandwidth": 600,
            "has_landline_phone": True,
        }

        # ADSL product
        self.adsl_product = self.browse_ref("somconnexio.ADSL20MBSenseFix")
        # The 20 Mb product attribute value already exists in prod DB
        self.expected_adsl_product_info = {
            "code": self.adsl_product.default_code,
            "name": self.adsl_product.showed_name,
            "price": self.demo_pricelist._get_products_price(
                self.adsl_product,
                1,
            ).get(self.adsl_product.id, 0.0),
            "category": "adsl",
            "minutes": None,
            "data": None,
            "bandwidth": 20,
            "has_landline_phone": False,
        }

    def _get_service_products(self):
        service_product_templates = self.env["product.template"].search(
            [
                (
                    "categ_id",
                    "in",
                    [
                        self.env.ref("somconnexio.mobile_service").id,
                        self.env.ref("somconnexio.broadband_adsl_service").id,
                        self.env.ref("somconnexio.broadband_fiber_service").id,
                    ],
                )
            ]
        )
        service_products = self.env["product.product"].search(
            [
                (
                    "product_tmpl_id",
                    "in",
                    [tmpl.id for tmpl in service_product_templates],
                ),
                ("public", "=", True),
            ]
        )
        return service_products

    def test_route(self):
        response = self.http_get(self.url, params=self.params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason, "OK")

    def test_price_list_content(self):
        response = self.http_get(self.url, params=self.params)
        content = json.loads(response.content.decode("utf-8"))

        obtained_pricelist = content.get("pricelists")[0].get("products")
        service_products = self._get_service_products()

        self.assertEqual(len(service_products), len(obtained_pricelist))
        self.assertIn(self.expected_mobile_product_info, obtained_pricelist)
        self.assertIn(self.expected_fiber_product_info, obtained_pricelist)
        self.assertIn(self.expected_adsl_product_info, obtained_pricelist)

    def test_search_by_code(self):
        response = self.http_get(self.url, params=self.params)

        content = json.loads(response.content.decode("utf-8"))
        obtained_pricelists = content.get("pricelists")
        self.assertEqual(len(obtained_pricelists), 1)
        self.assertEqual(obtained_pricelists[0].get("code"), self.code)

    def test_search_by_category(self):
        mobile_product_templ = self.env.ref("somconnexio.Mobile_product_template")
        mobile_products = self.env["product.product"].search(
            [
                ("product_tmpl_id", "=", mobile_product_templ.id),
                ("public", "=", True),
            ]
        )
        self.params["categ"] = "mobile"

        response = self.http_get(self.url, params=self.params)

        content = json.loads(response.content.decode("utf-8"))
        obtained_pricelists = content.get("pricelists")
        obtained_mobile_catalog = obtained_pricelists[0].get("products")
        self.assertEqual(len(obtained_pricelists), 1)
        self.assertEqual(len(obtained_mobile_catalog), len(mobile_products))
        self.assertEqual(obtained_mobile_catalog[0]["category"], "mobile")

    def test_search_by_is_company(self):
        particular_attr = self.env.ref("somconnexio.ParticularExclusive")
        fiber_product_templ = self.env.ref("somconnexio.Fibra_product_template")
        pack_product_templ = self.env.ref("somconnexio.Pack_product_template")
        fiber_products = self.env["product.product"].search(
            [
                ("product_tmpl_id", "=", fiber_product_templ.id),
                ("public", "=", True),
            ]
        )
        pack_products = self.env["product.product"].search(
            [
                ("product_tmpl_id", "=", pack_product_templ.id),
                ("public", "=", True),
            ]
        )
        fiber_ptav_particulars = self.env["product.template.attribute.value"].search(
            [
                ("product_tmpl_id", "=", fiber_product_templ.id),
                ("product_attribute_value_id", "=", particular_attr.id),
            ]
        )
        pack_ptav_particulars = self.env["product.template.attribute.value"].search(
            [
                ("product_tmpl_id", "=", pack_product_templ.id),
                ("product_attribute_value_id", "=", particular_attr.id),
            ]
        )
        fiber_products_not_particulars = fiber_products.filtered(
            lambda p: fiber_ptav_particulars
            not in p.product_template_attribute_value_ids
        )
        pack_products_not_particulars = pack_products.filtered(
            lambda p: pack_ptav_particulars
            not in p.product_template_attribute_value_ids
        )

        response = self.http_get(
            "{}?code={}&categ=fiber&is_company=true".format(self.url, self.code)
        )
        content = json.loads(response.content.decode("utf-8"))
        obtained_pricelists = content.get("pricelists")
        obtained_catalog = obtained_pricelists[0].get("products")
        obtained_catalog_packs = obtained_pricelists[0].get("packs")
        self.assertEqual(len(obtained_pricelists), 1)
        self.assertEqual(len(obtained_catalog), len(fiber_products_not_particulars))
        self.assertEqual(
            len(obtained_catalog_packs), len(pack_products_not_particulars)
        )

    def test_search_by_is_not_company(self):
        company_attr = self.env.ref("somconnexio.CompanyExclusive")
        fiber_product_templ = self.env.ref("somconnexio.Fibra_product_template")
        pack_product_templ = self.env.ref("somconnexio.Pack_product_template")
        fiber_products = self.env["product.product"].search(
            [
                ("product_tmpl_id", "=", fiber_product_templ.id),
                ("public", "=", True),
            ]
        )
        pack_products = self.env["product.product"].search(
            [
                ("product_tmpl_id", "=", pack_product_templ.id),
                ("public", "=", True),
            ]
        )

        fiber_ptav_company = self.env["product.template.attribute.value"].search(
            [
                ("product_tmpl_id", "=", fiber_product_templ.id),
                ("product_attribute_value_id", "=", company_attr.id),
            ]
        )
        pack_ptav_company = self.env["product.template.attribute.value"].search(
            [
                ("product_tmpl_id", "=", pack_product_templ.id),
                ("product_attribute_value_id", "=", company_attr.id),
            ]
        )

        fiber_products_not_company = fiber_products.filtered(
            lambda p: fiber_ptav_company not in p.product_template_attribute_value_ids
        )
        pack_products_not_company = pack_products.filtered(
            lambda p: pack_ptav_company not in p.product_template_attribute_value_ids
        )

        response = self.http_get(
            "{}?code={}&categ=fiber&is_company=false".format(self.url, self.code)
        )
        content = json.loads(response.content.decode("utf-8"))
        obtained_pricelists = content.get("pricelists")
        obtained_catalog = obtained_pricelists[0].get("products")
        obtained_catalog_packs = obtained_pricelists[0].get("packs")
        self.assertEqual(len(obtained_pricelists), 1)
        self.assertEqual(len(obtained_catalog), len(fiber_products_not_company))
        self.assertEqual(len(obtained_catalog_packs), len(pack_products_not_company))

    def test_search_catalan(self):
        response = self.http_get(
            self.url, headers={"Accept-Language": "ca_ES"}, params=self.params
        )
        content = json.loads(response.content.decode("utf-8"))
        obtained_pricelist = content.get("pricelists")[0].get("products")
        service_products = self._get_service_products()

        self.assertEqual(len(service_products), len(obtained_pricelist))
        self.assertIn(self.expected_mobile_product_info, obtained_pricelist)
        self.assertIn(self.expected_fiber_product_info, obtained_pricelist)
        self.assertIn(self.expected_adsl_product_info, obtained_pricelist)

    @mute_logger("odoo.addons.base_rest.http")
    def test_search_filtering_by_products_availables_from_product(self):
        fiber100sensefix_product = self.browse_ref("somconnexio.SenseFixFibra100Mb")
        fiber100sensefix_product.public = True
        expected_fiber_product_info = {
            "code": fiber100sensefix_product.default_code,
            "name": fiber100sensefix_product.showed_name,
            "price": self.demo_pricelist._get_products_price(
                fiber100sensefix_product,
                1,
            ).get(fiber100sensefix_product.id, 0.0),
            "category": "fiber",
            "minutes": None,
            "data": None,
            "bandwidth": 100,
            "has_landline_phone": False,
        }
        fiber100_product = self.browse_ref("somconnexio.Fibra100Mb")
        self.params["product_code"] = fiber100_product.default_code

        response = self.http_get(self.url, params=self.params)

        content = json.loads(response.content.decode("utf-8"))
        obtained_pricelist = content.get("pricelists")[0].get("products")

        self.assertIn(expected_fiber_product_info, obtained_pricelist)

    @mute_logger("odoo.addons.base_rest.http")
    def test_search_raise_error_incompatible_code_product_code(self):
        self.params.update(
            {
                "product_code": "PRODUCT_CODE",
                "categ": "CATEG",
            }
        )

        response = self.http_get(self.url, params=self.params)

        self.assertEqual(response.status_code, 400)
        error_msg = response.json().get("description")
        self.assertRegex(
            html.unescape(error_msg),
            "must not be present with",
        )

    @patch(
        "odoo.addons.somconnexio.models.catalog_service.CatalogService.pack_products"
    )
    def test_price_list_content_pack(self, mock_pack_products):
        pack_product = self.browse_ref("somconnexio.PackSenseFixFibra300MbIL30GB")
        mock_pack_products.return_value = pack_product
        fiber_pack_line = self.browse_ref(
            "somconnexio.PackSenseFixFibra300MbIL30GB_components_fibra"
        )
        component_fiber_product = fiber_pack_line.product_id
        mobile_pack_line = self.browse_ref(
            "somconnexio.PackSenseFixFibra300MbIL30GB_components_mobile"
        )
        component_mobile_product = mobile_pack_line.product_id

        expected_pack_component_fiber_info = {
            "code": component_fiber_product.default_code,
            "name": component_fiber_product.showed_name,
            "price": self.demo_pricelist._get_products_price(
                component_fiber_product,
                1,
            ).get(component_fiber_product.id, 0.0),
            "category": "fiber",
            "minutes": None,
            "data": None,
            "bandwidth": int(component_fiber_product.get_catalog_name("Bandwidth")),
            "has_landline_phone": not component_fiber_product.without_fix,
        }
        expected_pack_component_mobile_info = {
            "code": component_mobile_product.default_code,
            "name": component_mobile_product.showed_name,
            "price": self.demo_pricelist._get_products_price(
                component_mobile_product,
                1,
            ).get(component_mobile_product.id, 0.0),
            "category": "mobile",
            "minutes": 99999,
            "data": int(component_mobile_product.get_catalog_name("Data")),
            "bandwidth": None,
        }
        expected_pack_product_info = {
            "code": pack_product.default_code,
            "name": pack_product.showed_name,
            "price": 32.5,
            "category": "bonified_mobile",
            "mobiles_in_pack": int(mobile_pack_line.quantity),
            "fiber_bandwidth": int(
                component_fiber_product.get_catalog_name("Bandwidth")
            ),
            "has_land_line": not component_fiber_product.without_fix,
        }
        pack_product.public = True
        response = self.http_get(self.url)
        content = json.loads(response.content.decode("utf-8"))
        pricelist = content.get("pricelists")[0]
        self.assertTrue("packs" in pricelist)
        pack = [
            pack
            for pack in pricelist["packs"]
            if pack["code"] == expected_pack_product_info["code"]
        ]
        self.assertTrue(pack)
        pack = pack[0]
        self.assertIn("products", pack)
        products = pack["products"]
        del pack["products"]
        self.assertEqual(expected_pack_product_info, pack)
        self.assertIn(expected_pack_component_mobile_info, products)
        self.assertIn(expected_pack_component_fiber_info, products)
        self.assertEqual(len(products), 2)

    @patch(
        "odoo.addons.somconnexio.models.catalog_service.CatalogService.service_products"
    )
    def test_price_list_offer_attribute(self, mock_service_products):
        product_with_offer = self.browse_ref("somconnexio.TrucadesIllimitades20GB")
        mock_service_products.return_value = self.browse_ref(
            "somconnexio.TrucadesIllimitades20GB"
        )
        offer_product = self.browse_ref("somconnexio.TrucadesIllimitades20GBPack")
        expected_mobile_product_info = {
            "code": product_with_offer.default_code,
            "name": product_with_offer.showed_name,
            "price": self.demo_pricelist._get_products_price(
                product_with_offer,
                1,
            ).get(product_with_offer.id, 0.0),
            "category": "mobile",
            "minutes": 99999,
            "data": int(product_with_offer.get_catalog_name("Data")),
            "bandwidth": None,
            "offer": {
                "code": offer_product.default_code,
                "price": self.demo_pricelist._get_products_price(
                    offer_product,
                    1,
                ).get(offer_product.id, 0.0),
                "name": offer_product.showed_name,
            },
        }

        response = self.http_get(self.url)
        content = json.loads(response.content.decode("utf-8"))
        obtained_pricelist = content.get("pricelists")[0].get("products")

        self.assertTrue(expected_mobile_product_info in obtained_pricelist)

    @patch(
        "odoo.addons.somconnexio.models.catalog_service.CatalogService.pack_products"
    )
    def test_price_list_content_shared_bond(self, mock_pack_products):
        compartides_pack_product = self.browse_ref(
            "somconnexio.CompartidesFibra1Gb3mobils120GB"
        )
        component_fiber_product = self.browse_ref("somconnexio.Fibra1Gb")
        mobile_pack_line = self.env.ref(
            "somconnexio.CompartidesFibra1Gb3mobils120GB_components_mobile"
        )
        component_mobile_product = mobile_pack_line.product_id

        expected_pack_component_fiber_info = {
            "code": component_fiber_product.default_code,
            "name": component_fiber_product.showed_name,
            "price": self.demo_pricelist._get_products_price(
                component_fiber_product,
                1,
            ).get(component_fiber_product.id, 0.0),
            "category": "fiber",
            "minutes": None,
            "data": None,
            "bandwidth": int(component_fiber_product.get_catalog_name("Bandwidth")),
            "has_landline_phone": True,
        }
        expected_pack_component_mobile_info = {
            "code": component_mobile_product.default_code,
            "name": component_mobile_product.showed_name,
            "price": self.demo_pricelist._get_products_price(
                component_mobile_product,
                1,
            ).get(component_mobile_product.id, 0.0),
            "category": "mobile",
            "minutes": 99999,
            "data": int(component_mobile_product.get_catalog_name("Data")),
            "bandwidth": None,
        }
        expected_compartides_pack_product_info = {
            "code": compartides_pack_product.default_code,
            "name": compartides_pack_product.showed_name,
            "price": 61.0,
            "category": "mobile_shared_data",
            "mobiles_in_pack": int(mobile_pack_line.quantity),
            "fiber_bandwidth": int(
                component_fiber_product.get_catalog_name("Bandwidth")
            ),
            "has_land_line": not component_fiber_product.without_fix,
        }
        mock_pack_products.return_value = compartides_pack_product

        response = self.http_get(self.url)

        content = json.loads(response.content.decode("utf-8"))
        pricelist = content.get("pricelists")[0]
        self.assertTrue("packs" in pricelist)
        pack = [
            pack
            for pack in pricelist["packs"]
            if pack["code"] == expected_compartides_pack_product_info["code"]
        ]
        self.assertTrue(pack)

        pack = pack[0]
        self.assertIn("products", pack)

        products = pack["products"]
        del pack["products"]
        self.assertEqual(expected_compartides_pack_product_info, pack)
        self.assertIn(expected_pack_component_mobile_info, products)
        self.assertIn(expected_pack_component_fiber_info, products)
        self.assertEqual(len(products), 4)
