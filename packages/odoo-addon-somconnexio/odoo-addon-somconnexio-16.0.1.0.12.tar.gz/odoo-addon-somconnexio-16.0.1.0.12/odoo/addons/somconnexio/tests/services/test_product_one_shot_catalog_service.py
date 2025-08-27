import json

from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin


class TestProductOneShotCatalogController(BaseRestCaseAdmin):
    def setUp(self):
        super().setUp()
        self.url = "/api/one-shot-catalog"

    def test_route(self):
        response = self.http_get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason, "OK")

    def test_content(self):
        response = self.http_get(self.url + "/?product_code=SE_SC_REC_MOBILE_T_0_0")
        content = json.loads(response.content.decode("utf-8"))
        one_shots = content.get("pricelists")[0].get("one_shots")

        expected_1GB_one_shot = {
            "code": "CH_SC_OSO_1GB_ADDICIONAL",
            "name": "1 GB Addicionals",
            "price": 1.0,
            "minutes": 0,
            "data": 1024,
        }
        expected_3GB_one_shot = {
            "code": "CH_SC_OSO_3GB_ADDICIONAL",
            "name": "3 GB Addicionals",
            "price": 1.0,
            "minutes": 0,
            "data": 3072,
        }

        self.assertIn(expected_1GB_one_shot, one_shots)
        self.assertIn(expected_3GB_one_shot, one_shots)

    def test_content_sharing_tariff(self):
        response = self.http_get(
            self.url + "/?product_code=SE_SC_REC_MOBILE_2_SHARED_UNL_51200"
        )
        content = json.loads(response.content.decode("utf-8"))

        one_shots = content.get("pricelists")[0].get("one_shots")

        expected_10GB_one_shot = {
            "code": "CH_SC_OSO_SHARED_10GB_ADDICIONAL",
            "name": "10 GB Addicionals Compartides",
            "price": 1,
            "minutes": 0,
            "data": 10240,
        }
        expected_20GB_one_shot = {
            "code": "CH_SC_OSO_SHARED_20GB_ADDICIONAL",
            "name": "20 GB Addicionals Compartides",
            "price": 1,
            "minutes": 0,
            "data": 20480,
        }

        self.assertIn(expected_10GB_one_shot, one_shots)
        self.assertIn(expected_20GB_one_shot, one_shots)
