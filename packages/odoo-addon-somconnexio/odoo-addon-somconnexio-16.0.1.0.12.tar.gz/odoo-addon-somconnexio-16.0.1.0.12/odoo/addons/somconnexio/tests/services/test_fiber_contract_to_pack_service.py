from datetime import date

from odoo.exceptions import MissingError

from ..sc_test_case import SCTestCase
from ..helper_service import (
    crm_lead_create,
    contract_fiber_create_data,
    contract_mobile_create_data,
)


class FiberContractToPackServiceTestCase(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.Contract = self.env["contract.contract"]
        self.partner = self.browse_ref("somconnexio.res_partner_2_demo")
        self.vals_contract = contract_fiber_create_data(self.env, self.partner)
        self.fiber_contract_to_pack_service = self.env["fiber.contract.to.pack.service"]

    def test_get_fiber_contract_to_pack_partner_not_found(self):
        self.assertRaisesRegex(
            MissingError,
            "Partner with ref fake_ref not found",
            self.fiber_contract_to_pack_service.create,
            partner_ref="fake_ref",
        )

    def test_get_fiber_contract_to_pack_no_fiber_contract_to_pack(
        self,
    ):
        self.assertRaisesRegex(
            MissingError,
            "No fiber contracts available to pack found with this user",
            self.fiber_contract_to_pack_service.create,
            partner_ref=self.partner.ref,
            mobile_sharing_data="false",
        )

    def test_get_fiber_contract_to_pack_filter_fibers_used_in_ODOO_lead_lines(self):
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

        filtered_contracts = self.fiber_contract_to_pack_service.create(
            partner_ref=self.partner.ref,
        )

        self.assertEqual(len(filtered_contracts), 2)
        self.assertIn(first_fiber_contract, filtered_contracts)
        self.assertNotIn(second_fiber_contract, filtered_contracts)
        self.assertIn(third_fiber_contract, filtered_contracts)

    def test_get_fiber_contracts_not_found_technology(self):
        """ """
        mbl_vals_contract = contract_mobile_create_data(self.env, self.partner)
        self.Contract.create(mbl_vals_contract)

        self.assertRaisesRegex(
            MissingError,
            "No fiber contracts available to pack found with this user",
            self.fiber_contract_to_pack_service.create,
            partner_ref=self.partner.ref,
            mobile_sharing_data="false",
        )

    def test_get_fiber_contracts_to_pack_ref_terminated(self):
        fiber_contract = self.Contract.create(self.vals_contract)
        fiber_contract.write(
            {
                "is_terminated": True,
                "date_end": date.today(),
            }
        )
        self.assertRaisesRegex(
            MissingError,
            "No fiber contracts available to pack found with this user",
            self.fiber_contract_to_pack_service.create,
            partner_ref=self.partner.ref,
            mobile_sharing_data="false",
        )

    def test_get_fiber_contracts_to_pack_two(self):
        first_fiber_contract = self.Contract.create(self.vals_contract)
        second_fiber_contract = self.Contract.create(self.vals_contract)

        contracts = self.fiber_contract_to_pack_service.create(
            partner_ref=self.partner.ref
        )
        self.assertEqual(len(contracts), 2)
        self.assertIn(first_fiber_contract, contracts)
        self.assertIn(second_fiber_contract, contracts)

    def test_get_fiber_contracts_to_pack_mobiles_sharing_data(self):
        fiber_contract_in_pack = self.browse_ref("somconnexio.contract_fibra_600_pack")
        fiber_contract = self.browse_ref("somconnexio.contract_fibra_600")

        contracts = self.fiber_contract_to_pack_service.create(
            partner_ref=fiber_contract.partner_id.ref, mobiles_sharing_data="true"
        )

        self.assertEqual(len(contracts), 2)
        self.assertIn(fiber_contract, contracts)
        self.assertIn(fiber_contract_in_pack, contracts)

    def test_get_fiber_contracts_to_pack_all(self):
        fiber_contract_shared = self.browse_ref("somconnexio.contract_fibra_600_shared")
        fiber_contract_in_pack = self.browse_ref("somconnexio.contract_fibra_600_pack")
        fiber_contract = self.browse_ref("somconnexio.contract_fibra_600")

        contracts = self.fiber_contract_to_pack_service.create(
            partner_ref=fiber_contract.partner_id.ref, all="true"
        )

        self.assertEqual(len(contracts), 5)
        self.assertIn(fiber_contract, contracts)
        self.assertIn(fiber_contract_in_pack, contracts)
        self.assertIn(fiber_contract_shared, contracts)

    def test_get_fiber_contracts_not_found_already_packed(self):
        # Fiber contract already linked to a bonified mobile (pack)
        fiber_contract_unpacked = self.browse_ref("somconnexio.contract_fibra_600")
        partner = fiber_contract_unpacked.partner_id
        fiber_contract_unpacked.unlink()

        self.assertRaisesRegex(
            MissingError,
            "No fiber contracts available to pack found with this user",
            self.fiber_contract_to_pack_service.create,
            partner_ref=partner.ref,
            mobile_sharing_data="false",
        )
