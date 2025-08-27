from datetime import date

from ..sc_test_case import SCComponentTestCase

from ..helper_service import (
    contract_fiber_create_data,
    contract_mobile_create_data,
)


class TestContractListener(SCComponentTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.partner = self.env.ref("somconnexio.res_partner_2_demo")
        self.contract_data = contract_mobile_create_data(self.env, self.partner)
        group_can_terminate_contract = self.env.ref("contract.can_terminate_contract")
        group_can_terminate_contract.users |= self.env.user

    def _create_ba_contract(self):
        self.ba_contract = self.env["contract.contract"].create(
            contract_fiber_create_data(self.env, self.partner)
        )

    def test_terminate_pack(self):
        contract = self.browse_ref("somconnexio.contract_mobile_il_20_pack")
        ba_contract = contract.parent_pack_contract_id

        # Listener would be activated when date_end is set
        ba_contract.date_end = date.today()

        ba_contract.terminate_contract(
            self.browse_ref("somconnexio.reason_other"),
            "Comment",
            date.today(),
            self.browse_ref("somconnexio.user_reason_other"),
        )

        # Call to breack_pack
        self.assertFalse(contract.is_pack)
        self.assertFalse(contract.parent_pack_contract_id)

    def test_terminate_pack_address_change(self):
        contract = self.browse_ref("somconnexio.contract_mobile_il_20_pack")
        ba_contract = contract.parent_pack_contract_id

        # Listener would be activated when date_end is set
        ba_contract.date_end = date.today()

        ba_contract.terminate_contract(
            self.browse_ref("somconnexio.reason_location_change_from_SC_to_SC"),
            "Location change",
            date.today(),
            self.browse_ref("somconnexio.user_reason_other"),
        )

        # Not call to breack_pack
        self.assertTrue(contract.is_pack)
        self.assertEqual(contract.parent_pack_contract_id, ba_contract)
