import odoo
import json
from datetime import date, timedelta

from mock import Mock, patch
from otrs_somconnexio.otrs_models.configurations.changes.change_tariff import (
    ChangeTariffSharedBondTicketConfiguration,
    ChangeTariffTicketConfiguration,
)

from ....services.contract_contract_service import ContractService
from ...common_service import BaseRestCaseAdmin
from ...helper_service import crm_lead_create, contract_fiber_create_data


class TestContractGetFiberContractsNotPackedController(BaseRestCaseAdmin):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.Contract = self.env["contract.contract"]

        self.partner = self.browse_ref("somconnexio.res_partner_2_demo")

        self.vals_contract = contract_fiber_create_data(self.env, self.partner)

        self.endpoint = "/api/contract/available-fibers-to-link-with-mobile"
        self.url = "{}?{}={}".format(self.endpoint, "partner_ref", self.partner.ref)

    def _null_side_effect(self, contracts):
        return contracts

    @patch(
        "odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_OTRS_tickets"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_ODOO_lead_lines"  # noqa
    )
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_to_pack_ref_ok(
        self, mock_filter_ODOO_lead_lines, mock_filter_OTRS_tickets
    ):
        mock_filter_OTRS_tickets.side_effect = self._null_side_effect
        mock_filter_ODOO_lead_lines.side_effect = self._null_side_effect

        fiber_contract = self.Contract.create(self.vals_contract)

        response = self.http_get(self.url)

        self.assertEqual(response.status_code, 200)

        result = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], fiber_contract.id)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_to_pack_ref_terminated(self):
        fiber_contract = self.Contract.create(self.vals_contract)
        fiber_contract.write(
            {
                "is_terminated": True,
                "date_end": date.today(),
            }
        )
        response = self.http_get(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.reason, "NOT FOUND")

    @patch(
        "odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_OTRS_tickets"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_ODOO_lead_lines"  # noqa
    )
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_to_pack_two(
        self, mock_filter_ODOO_lead_lines, mock_filter_OTRS_tickets
    ):
        mock_filter_OTRS_tickets.side_effect = self._null_side_effect
        mock_filter_ODOO_lead_lines.side_effect = self._null_side_effect

        first_fiber_contract = self.Contract.create(self.vals_contract)
        second_fiber_contract = self.Contract.create(self.vals_contract)

        response = self.http_get(self.url)

        self.assertEqual(response.status_code, 200)

        result = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(result), 2)
        resulting_ids = [r["id"] for r in result]
        self.assertIn(first_fiber_contract.id, resulting_ids)
        self.assertIn(second_fiber_contract.id, resulting_ids)

    @patch(
        "odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_OTRS_tickets"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_ODOO_lead_lines"  # noqa
    )
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_to_pack_one_already_in_pack(
        self, mock_filter_ODOO_lead_lines, mock_filter_OTRS_tickets
    ):
        mock_filter_OTRS_tickets.side_effect = self._null_side_effect
        mock_filter_ODOO_lead_lines.side_effect = self._null_side_effect

        fiber_contract_in_pack = self.browse_ref("somconnexio.contract_fibra_600_pack")
        fiber_contract = self.browse_ref("somconnexio.contract_fibra_600")
        partner_id = fiber_contract.partner_id

        url = "{}?{}={}".format(self.endpoint, "partner_ref", partner_id.ref)

        response = self.http_get(url)

        self.assertEqual(response.status_code, 200)

        result = json.loads(response.content.decode("utf-8"))
        contract_ids = [c["id"] for c in result]

        self.assertEqual(len(contract_ids), 1)
        self.assertIn(fiber_contract.id, contract_ids)
        self.assertNotIn(fiber_contract_in_pack.id, contract_ids)

    @patch(
        "odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_OTRS_tickets"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_ODOO_lead_lines"  # noqa
    )
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_to_pack_mobiles_sharing_data(
        self, mock_filter_ODOO_lead_lines, mock_filter_OTRS_tickets
    ):
        mock_filter_OTRS_tickets.side_effect = self._null_side_effect
        mock_filter_ODOO_lead_lines.side_effect = self._null_side_effect

        fiber_contract_in_pack = self.browse_ref("somconnexio.contract_fibra_600_pack")
        fiber_contract = self.browse_ref("somconnexio.contract_fibra_600")

        url = "{}?{}={}".format(
            self.endpoint, "partner_ref", fiber_contract.partner_id.ref
        )

        response = self.http_get(url + "&mobiles_sharing_data=true")
        self.assertEqual(response.status_code, 200)

        result = json.loads(response.content.decode("utf-8"))
        contract_ids = [c["id"] for c in result]

        self.assertEqual(len(contract_ids), 2)
        self.assertIn(fiber_contract.id, contract_ids)
        self.assertIn(fiber_contract_in_pack.id, contract_ids)

    @patch(
        "odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_OTRS_tickets"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_ODOO_lead_lines"  # noqa
    )
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_not_found_other_partner(
        self, mock_filter_ODOO_lead_lines, mock_filter_OTRS_tickets
    ):
        mock_filter_OTRS_tickets.side_effect = self._null_side_effect
        mock_filter_ODOO_lead_lines.side_effect = self._null_side_effect

        other_partner_id = self.env.ref("somconnexio.res_partner_1_demo")
        vals_contract = self.vals_contract.copy()
        vals_contract.update(
            {
                "partner_id": other_partner_id.id,
                "invoice_partner_id": other_partner_id.id,
                "service_partner_id": other_partner_id.id,
                "mandate_id": other_partner_id.bank_ids[0].mandate_ids[0].id,
                "email_ids": [(4, other_partner_id.id, 0)],
            }
        )
        self.Contract.create(vals_contract)

        response = self.http_get(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.reason, "NOT FOUND")

    @patch(
        "odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_OTRS_tickets"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_ODOO_lead_lines"  # noqa
    )
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_not_found_already_packed(
        self, mock_filter_ODOO_lead_lines, mock_filter_OTRS_tickets
    ):
        mock_filter_OTRS_tickets.side_effect = self._null_side_effect
        mock_filter_ODOO_lead_lines.side_effect = self._null_side_effect

        # Fiber contract already linked to a bonified mobile (pack)
        fiber_contract_packed = self.browse_ref("somconnexio.contract_fibra_600_pack")
        fiber_contract_unpacked = self.browse_ref("somconnexio.contract_fibra_600")
        fiber_contract_unpacked.unlink()

        url = "{}?{}={}".format(
            self.endpoint, "partner_ref", fiber_contract_packed.partner_id.ref
        )
        response = self.http_get(url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.reason, "NOT FOUND")

    @patch(
        "odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_OTRS_tickets"  # noqa
    )
    @patch(
        "odoo.addons.somconnexio.services.contract_contract_service.ContractService._filter_out_fibers_used_in_ODOO_lead_lines"  # noqa
    )
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_not_found_technology(
        self, mock_filter_ODOO_lead_lines, mock_filter_OTRS_tickets
    ):
        mock_filter_OTRS_tickets.side_effect = self._null_side_effect
        mock_filter_ODOO_lead_lines.side_effect = self._null_side_effect

        mbl_contract_service_info = self.env["mobile.service.contract.info"].create(
            {
                "phone_number": "666777888",
                "icc": "123",
            }
        )
        mbl_product = self.browse_ref("somconnexio.150Min1GB")
        mbl_contract_line = {
            "name": mbl_product.name,
            "product_id": mbl_product.id,
            "date_start": "2020-01-01 00:00:00",
            "recurring_next_date": date.today() + timedelta(days=30),
        }
        mbl_vals_contract = self.vals_contract.copy()
        mbl_vals_contract.update(
            {
                "service_technology_id": self.ref(
                    "somconnexio.service_technology_mobile"
                ),
                "mm_fiber_service_contract_info_id": False,
                "service_supplier_id": self.env.ref(
                    "somconnexio.service_supplier_masmovil"
                ).id,
                "mobile_contract_service_info_id": mbl_contract_service_info.id,
                "contract_line_ids": [(0, False, mbl_contract_line)],
            }
        )
        self.Contract.create(mbl_vals_contract)

        response = self.http_get(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.reason, "NOT FOUND")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_not_found_no_partner(self):
        fake_partner_ref = "234252"
        url = "{}?{}={}".format(self.endpoint, "partner_ref", fake_partner_ref)
        response = self.http_get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.reason, "NOT FOUND")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_fiber_contracts_bad_request(self):
        url = "{}?{}={}".format(self.endpoint, "partner_nif", self.partner.ref)

        response = self.http_get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.reason, "BAD REQUEST")

    @patch(
        "odoo.addons.somconnexio.services.contract_contract_service.SearchTicketsService"  # noqa
    )
    def test_filter_out_fibers_used_in_OTRS_tickets(self, MockSearchTicketsService):
        fiber_contract_1 = self.browse_ref("somconnexio.contract_fibra_600_pack")
        fiber_contract_2 = self.browse_ref("somconnexio.contract_fibra_600")

        expected_dct = {
            "OdooContractRefRelacionat": [fiber_contract_1.code, fiber_contract_2.code]
        }

        mock_ticket = Mock(spec=["fiber_contract_code"])
        # A ticket with second_code referenced fiber_contract_code will be found
        mock_ticket.fiber_contract_code = fiber_contract_2.code

        MockSearchTicketsService.return_value = Mock(spec=["search"])
        MockSearchTicketsService.return_value.search.return_value = [mock_ticket]

        service = ContractService(self.env)
        filtered_contracts = service._filter_out_fibers_used_in_OTRS_tickets(
            fiber_contract_1 + fiber_contract_2
        )

        MockSearchTicketsService.assert_called_once_with(
            [
                ChangeTariffTicketConfiguration,
                ChangeTariffSharedBondTicketConfiguration,
            ]
        )
        MockSearchTicketsService.return_value.search.assert_called_once_with(  # noqa
            fiber_contract_1.partner_id.ref, df_dct=expected_dct
        )
        self.assertEqual(len(filtered_contracts), 1)
        # Only first fiber contract available
        self.assertEqual(filtered_contracts, fiber_contract_1)

    def test_filter_out_fibers_used_in_OTRS_tickets_empty(self):
        contracts = []
        service = ContractService(self.env)
        filtered_contracts = service._filter_out_fibers_used_in_OTRS_tickets(contracts)

        self.assertFalse(filtered_contracts)

    def test_filter_out_fibers_used_in_ODOO_lead_lines(self):
        first_fiber_contract = self.Contract.create(self.vals_contract)
        second_fiber_contract = self.Contract.create(self.vals_contract)
        third_fiber_contract = self.Contract.create(self.vals_contract)

        # Cancelled
        first_mbl_crm_lead = crm_lead_create(self.env, self.partner, "mobile")
        first_mbl_isp_info = first_mbl_crm_lead.lead_line_ids[0].mobile_isp_info
        first_mbl_isp_info.linked_fiber_contract_id = first_fiber_contract.id
        first_mbl_crm_lead.action_set_cancelled()

        # Already linked lead line
        second_mbl_crm_lead = crm_lead_create(self.env, self.partner, "mobile")
        second_mbl_isp_info = second_mbl_crm_lead.lead_line_ids[0].mobile_isp_info
        second_mbl_isp_info.linked_fiber_contract_id = second_fiber_contract.id

        # Unlinked lead line
        crm_lead_create(self.env, self.partner, "mobile")

        contract_service = ContractService(self.env)
        filtered_contracts = (
            contract_service._filter_out_fibers_used_in_ODOO_lead_lines(
                first_fiber_contract + second_fiber_contract + third_fiber_contract
            )
        )

        self.assertEqual(len(filtered_contracts), 2)
        self.assertIn(first_fiber_contract, filtered_contracts)
        self.assertNotIn(second_fiber_contract, filtered_contracts)
        self.assertIn(third_fiber_contract, filtered_contracts)

    def test_filter_out_fibers_used_in_ODOO_lead_lines_empty(self):
        contracts = []
        service = ContractService(self.env)
        filtered_contracts = service._filter_out_fibers_used_in_ODOO_lead_lines(
            contracts
        )

        self.assertFalse(filtered_contracts)
