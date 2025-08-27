from datetime import date

from ..sc_test_case import SCTestCase


class TestContractOneShotRequestWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.start_date = date.today()
        self.contract = self.env.ref("somconnexio.contract_mobile_il_20")
        self.partner = self.contract.partner_id
        self.user_admin = self.browse_ref("base.user_admin")

    def test_wizard_one_shot_request_sim(self):
        product = self.browse_ref("somconnexio.EnviamentSIM")
        contract_lines_before = len(self.contract.contract_line_ids)

        wizard = (
            self.env["contract.one.shot.request.wizard"]
            .with_context(active_id=self.contract.id)
            .with_user(self.user_admin)
            .sudo()
            .create(
                {
                    "start_date": self.start_date,
                    "one_shot_product_id": product.id,
                    "summary": "",
                    "done": False,
                }
            )
        )

        wizard.onchange_one_shot_product_id()
        partner_activities_before = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)]
        )
        wizard.button_add()
        partner_activities_after = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)],
        )
        self.assertEqual(
            len(partner_activities_after) - len(partner_activities_before), 1
        )
        created_activity = partner_activities_after[-1]
        self.assertEqual(created_activity.user_id, self.user_admin)
        self.assertEqual(
            created_activity.activity_type_id,
            self.browse_ref("somconnexio.mail_activity_type_sim_change"),
        )
        self.assertEqual(created_activity.done, wizard.done)
        self.assertEqual(created_activity.summary, wizard.summary)
        self.assertEqual(
            len(self.contract.contract_line_ids), contract_lines_before + 1
        )

    def test_wizard_one_shot_request_additional_sms(self):
        product = self.browse_ref("somconnexio.SMSMassius500SMS")
        contract_lines_before = len(self.contract.contract_line_ids)

        wizard = (
            self.env["contract.one.shot.request.wizard"]
            .with_context(active_id=self.contract.id)
            .with_user(self.user_admin)
            .sudo()
            .create(
                {
                    "start_date": self.start_date,
                    "one_shot_product_id": product.id,
                    "summary": "",
                    "done": False,
                }
            )
        )
        wizard.onchange_one_shot_product_id()
        partner_activities_before = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)]
        )
        wizard.button_add()
        partner_activities_after = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)],
        )
        self.assertEqual(
            len(partner_activities_after) - len(partner_activities_before), 1
        )
        created_activity = partner_activities_after[-1]
        self.assertEqual(created_activity.user_id, self.user_admin)
        self.assertEqual(
            created_activity.activity_type_id,
            self.browse_ref("somconnexio.mail_activity_type_one_shot"),
        )
        self.assertEqual(created_activity.done, wizard.done)
        self.assertEqual(created_activity.summary, wizard.summary)
        self.assertEqual(
            len(self.contract.contract_line_ids), contract_lines_before + 1
        )

    def test_wizard_one_shot_request_data_without_cost(self):
        product = self.browse_ref("somconnexio.DadesAddicionals1GBSenseCost")
        contract_lines_before = len(self.contract.contract_line_ids)

        wizard = (
            self.env["contract.one.shot.request.wizard"]
            .with_context(active_id=self.contract.id)
            .with_user(self.user_admin)
            .sudo()
            .create(
                {
                    "start_date": self.start_date,
                    "one_shot_product_id": product.id,
                    "summary": "",
                    "done": False,
                }
            )
        )
        wizard.onchange_one_shot_product_id()
        partner_activities_before = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)]
        )
        wizard.button_add()
        partner_activities_after = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)],
        )
        self.assertEqual(
            len(partner_activities_after) - len(partner_activities_before), 1
        )
        created_activity = partner_activities_after[-1]
        self.assertEqual(created_activity.user_id, self.user_admin)
        self.assertEqual(
            created_activity.activity_type_id,
            self.browse_ref("somconnexio.mail_activity_type_one_shot"),
        )
        self.assertEqual(created_activity.done, wizard.done)
        self.assertEqual(created_activity.summary, wizard.summary)
        self.assertEqual(
            len(self.contract.contract_line_ids), contract_lines_before + 1
        )

    def test_wizard_one_shot_request_send_return_router(self):
        self.contract = self.env.ref("somconnexio.contract_fibra_600")
        self.partner = self.contract.partner_id
        contract_lines_before = len(self.contract.contract_line_ids)

        product = self.browse_ref("somconnexio.EnviamentRouter")
        wizard = (
            self.env["contract.one.shot.request.wizard"]
            .with_context(active_id=self.contract.id)
            .with_user(self.user_admin)
            .sudo()
            .create(
                {
                    "start_date": self.start_date,
                    "one_shot_product_id": product.id,
                    "summary": "test",
                    "done": False,
                }
            )
        )
        wizard.onchange_one_shot_product_id()
        partner_activities_before = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)]
        )
        wizard.button_add()
        partner_activities_after = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)],
        )
        self.assertEqual(
            len(partner_activities_after) - len(partner_activities_before), 1
        )
        created_activity = partner_activities_after[-1]
        self.assertEqual(created_activity.user_id, self.user_admin)
        self.assertEqual(
            created_activity.activity_type_id,
            self.browse_ref("somconnexio.mail_activity_type_router_send_or_return"),
        )
        self.assertEqual(created_activity.done, wizard.done)
        self.assertEqual(created_activity.summary, wizard.summary)
        self.assertEqual(
            len(self.contract.contract_line_ids), contract_lines_before + 1
        )

    def test_wizard_one_shot_request_send_return_router_4g(self):
        self.contract = self.env.ref("somconnexio.contract_4G")
        self.partner = self.contract.partner_id
        contract_lines_before = len(self.contract.contract_line_ids)

        product = self.browse_ref("somconnexio.EnviamentRouter")
        wizard = (
            self.env["contract.one.shot.request.wizard"]
            .with_context(active_id=self.contract.id)
            .with_user(self.user_admin)
            .sudo()
            .create(
                {
                    "start_date": self.start_date,
                    "one_shot_product_id": product.id,
                    "summary": "test",
                    "done": False,
                }
            )
        )

        wizard.onchange_one_shot_product_id()
        partner_activities_before = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)]
        )
        wizard.button_add()
        partner_activities_after = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)],
        )
        self.assertEqual(
            len(partner_activities_after) - len(partner_activities_before), 1
        )
        created_activity = partner_activities_after[-1]
        self.assertEqual(created_activity.user_id, self.user_admin)
        self.assertEqual(
            created_activity.activity_type_id,
            self.browse_ref("somconnexio.mail_activity_type_router_send_or_return"),
        )
        self.assertEqual(created_activity.done, wizard.done)
        self.assertEqual(created_activity.summary, wizard.summary)
        self.assertEqual(
            len(self.contract.contract_line_ids), contract_lines_before + 1
        )

    def test_wizard_one_shot_request_sign_up_exisiting_pair(self):
        self.contract = self.env.ref("somconnexio.contract_adsl")
        self.partner = self.contract.partner_id
        contract_lines_before = len(self.contract.contract_line_ids)

        product = self.env.ref("somconnexio.AltaParellExistent")
        wizard = (
            self.env["contract.one.shot.request.wizard"]
            .with_context(active_id=self.contract.id)
            .with_user(self.user_admin)
            .sudo()
            .create(
                {
                    "start_date": self.start_date,
                    "one_shot_product_id": product.id,
                    "summary": "test",
                    "done": False,
                }
            )
        )

        wizard.button_add()

        self.assertEqual(
            len(self.contract.contract_line_ids), contract_lines_before + 1
        )

    def test_add_one_shot_to_contract(self):
        product = self.env.ref("somconnexio.EnviamentSIM")
        contract_lines_before = len(self.contract.contract_line_ids)

        wizard = (
            self.env["contract.one.shot.request.wizard"]
            .with_context(active_id=self.contract.id)
            .create(
                {
                    "start_date": self.start_date,
                    "one_shot_product_id": product.id,
                    "summary": "Test One Shot Summary",
                    "done": False,
                }
            )
        )

        wizard.onchange_one_shot_product_id()
        wizard.button_add()

        activity = self.env["mail.activity"].search(
            [
                ("res_id", "=", self.contract.id),
                ("res_model", "=", "contract.contract"),
                ("summary", "=", wizard.summary),
            ]
        )

        self.assertEqual(
            activity.activity_type_id,
            self.browse_ref("somconnexio.mail_activity_type_sim_change"),
        )
        self.assertFalse(activity.done)

        self.assertEqual(
            len(self.contract.contract_line_ids),
            contract_lines_before + 1,
        )
        self.assertEqual(self.contract.contract_line_ids[1].product_id, product)
        # TODO -> Check why:
        # self.contract_id.write(
        #   {"contract_line_ids": [(0, 0, one_shot_contract_line)]}
        # )
        # overrides the input date_start and sets it as the first contract line
        # self.assertEqual(
        #   self.contract.contract_line_ids[1].date_start, self.start_date
        # )

    def test_available_products_mobile_sharing_data_contract(self):
        contract = self.env.ref("somconnexio.contract_mobile_il_50_shared_1_of_2")
        sharing_product = self.env.ref("somconnexio.DadesAddicionals10GBCompartides")

        wizard = (
            self.env["contract.one.shot.request.wizard"]
            .with_context(active_id=contract.id)
            .create(
                {
                    "start_date": self.start_date,
                    "one_shot_product_id": sharing_product.id,
                    "summary": "Test Summary",
                    "done": False,
                }
            )
        )

        self.assertIn(sharing_product, wizard.available_products)

    def test_available_products_mobile_non_sharing_data_contract(self):
        product = self.env.ref("somconnexio.DadesAddicionals500MB")
        sharing_product = self.env.ref("somconnexio.DadesAddicionals10GBCompartides")

        wizard = (
            self.env["contract.one.shot.request.wizard"]
            .with_context(active_id=self.contract.id)
            .create(
                {
                    "start_date": self.start_date,
                    "one_shot_product_id": product.id,
                    "summary": "Test Summary",
                    "done": False,
                }
            )
        )

        self.assertNotIn(sharing_product, wizard.available_products)
