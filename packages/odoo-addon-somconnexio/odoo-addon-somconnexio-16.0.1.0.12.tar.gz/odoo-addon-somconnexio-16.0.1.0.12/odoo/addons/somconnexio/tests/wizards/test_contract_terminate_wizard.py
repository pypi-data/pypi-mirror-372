from datetime import date
from ..sc_test_case import SCTestCase


class TestContractTerminateWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.terminate_reason = self.env["contract.terminate.reason"].create(
            {"name": "terminate_reason"}
        )
        self.terminate_user_reason = self.env["contract.terminate.reason"].create(
            {"name": "terminate_user_reason"}
        )

    def test_wizard_terminate_contract_user_reason(self):
        contract = self.env.ref("somconnexio.contract_mobile_il_20")
        terminate_date = date.today()
        wizard = (
            self.env["contract.terminate.wizard"]
            .with_context(active_id=contract.id)
            .create(
                {
                    "terminate_date": terminate_date,
                    "terminate_reason_id": self.terminate_reason.id,
                    "terminate_user_reason_id": self.terminate_user_reason.id,
                }
            )
        )

        wizard.terminate_contract()
        self.assertTrue(contract.is_terminated)
        self.assertEqual(contract.terminate_date, terminate_date)
        self.assertEqual(
            contract.terminate_user_reason_id.id, self.terminate_user_reason.id
        )
        contract.action_cancel_contract_termination()
        self.assertFalse(contract.is_terminated)
        self.assertFalse(contract.terminate_reason_id)
        self.assertFalse(contract.terminate_user_reason_id)
        self.assertFalse(wizard.is_fiber_contract_in_pack)

    def test_will_force_other_mobiles_to_quit_pack_with_mobile_contract_bonds(self):
        mobile_contract = self.env.ref(
            "somconnexio.contract_mobile_il_50_shared_1_of_3"
        )
        wizard_action = self.env["contract.termination.wizard"].create(
            {"contract_id": mobile_contract.id}
        )

        self.assertTrue(wizard_action.will_force_other_mobiles_to_quit_pack)

    def test_will_force_other_mobiles_to_quit_pack_with_fiber_contract_and_bonds(self):
        fiber_contract_with_mobiles = self.env.ref(
            "somconnexio.contract_fibra_600_pack"
        )
        wizard_action = self.env["contract.termination.wizard"].create(
            {"contract_id": fiber_contract_with_mobiles.id}
        )

        self.assertTrue(wizard_action.will_force_other_mobiles_to_quit_pack)

    def test_will_force_other_mobiles_to_quit_pack_with_mobile_contract_no_bonds(self):
        mobile_contract_without_bonds = self.env.ref(
            "somconnexio.contract_mobile_il_50_shared_3_of_3"
        )
        wizard_action = self.env["contract.termination.wizard"].create(
            {"contract_id": mobile_contract_without_bonds.id}
        )

        self.assertFalse(wizard_action.will_force_other_mobiles_to_quit_pack)

    def test_will_force_other_mobiles_to_quit_pack_with_fiber_contract_no_bonds(self):
        fiber_contract_without_mobiles = self.env.ref("somconnexio.contract_fibra_1000")
        wizard_action = self.env["contract.termination.wizard"].create(
            {"contract_id": fiber_contract_without_mobiles.id}
        )

        self.assertFalse(wizard_action.will_force_other_mobiles_to_quit_pack)
