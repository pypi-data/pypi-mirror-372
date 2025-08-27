import json
import odoo

from odoo.addons.base_rest_somconnexio.tests.common_service import BaseRestCaseAdmin


class TestProviderController(BaseRestCaseAdmin):
    def setUp(self):
        super().setUp()
        self.previous_providers = self.env["previous.provider"].search([])

    def test_route_search_without_filter(self):
        url = "/api/provider"
        params = []

        response = self.http_get(url, params)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason, "OK")

        content = json.loads(response.content.decode("utf-8"))

        self.assertIn("providers", content)
        self.assertIn("count", content)
        self.assertEqual(content["count"], len(self.previous_providers))

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_mobile_search_parameter(self):
        url = "/api/provider?mobile=1"

        response = self.http_get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.reason, "BAD REQUEST")

        error = response.json()
        self.assertIn(
            "{&#x27;mobile&#x27;: [&#x27;Must be a boolean value: true or false&#x27;]}",  # noqa
            error["description"],
        )

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_bad_broadband_search_parameter(self):
        url = "/api/provider?broadband=t"

        response = self.http_get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.reason, "BAD REQUEST")

        error = response.json()
        self.assertIn(
            "{&#x27;broadband&#x27;: [&#x27;Must be a boolean value: true or false&#x27;]}",  # noqa
            error["description"],
        )

    def test_route_search_by_mobile(self):
        url = "/api/provider?mobile=true"
        mobile_previous_providers = self.previous_providers.filtered("mobile")

        content = self.http_get_content(url)

        self.assertEqual(content["count"], len(mobile_previous_providers))

    def test_route_search_by_broadband(self):
        url = "/api/provider?broadband=true"
        broadband_previous_providers = self.previous_providers.filtered("broadband")

        content = self.http_get_content(url)

        self.assertEqual(content["count"], len(broadband_previous_providers))

    def test_route_search_both_services(self):
        url = "/api/provider?mobile=true&broadband=true"

        mobile_broadband_previous_providers = [
            pp for pp in self.previous_providers if pp.mobile and pp.broadband
        ]

        content = self.http_get_content(url)

        self.assertEqual(content["count"], len(mobile_broadband_previous_providers))
