from datetime import date, timedelta
from mock import patch
from ..sc_test_case import SCTestCase
from odoo.exceptions import ValidationError


class TestContractTariffChangeWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.partner = self.browse_ref("somconnexio.res_partner_1_demo")
        self.contract = self.env.ref("somconnexio.contract_mobile_il_20")
        self.contract_ba = self.env.ref("somconnexio.contract_fibra_600")
        self.contract_ba_pack = self.env.ref("somconnexio.contract_fibra_600_pack")
        self.product_ba = self.contract_ba.current_tariff_product
        self.user_admin = self.browse_ref("base.user_admin")
        self.new_tariff_product_id = self.browse_ref("somconnexio.150Min2GB")
        self.new_tariff_ba_same_tech_product_id = self.browse_ref(
            "somconnexio.Fibra1Gb"
        )
        self.new_tariff_ba_different_tech_product_id = self.browse_ref(
            "somconnexio.ADSL20MBSenseFix"
        )
        self.new_tariff_ba_wo_fix_product_id = self.browse_ref(
            "somconnexio.SenseFixFibra100Mb"
        )

    def test_wizard_tariff_change_ok(self):
        self.assertEqual(
            self.contract.current_tariff_contract_line.product_id.id,
            self.ref("somconnexio.TrucadesIllimitades20GB"),
        )
        start_date = date.today()

        wizard = (
            self.env["contract.tariff.change.wizard"]
            .with_context(active_id=self.contract.id)
            .with_user(self.user_admin)
            .create(
                {
                    "start_date": start_date,
                    "summary": "Tariff change 150 min 2 GB",
                }
            )
        )
        wizard.new_tariff_product_id = self.new_tariff_product_id

        partner_activities_before = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)]
        )
        wizard.button_change()
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
            self.browse_ref("somconnexio.mail_activity_type_tariff_change"),
        )
        self.assertEqual(created_activity.done, True)
        self.assertEqual(
            created_activity.summary,
            "Tariff change {}".format(self.new_tariff_product_id.showed_name),
        )
        self.assertTrue(self.contract.current_tariff_contract_line)
        self.assertTrue(self.contract.contract_line_ids[0].date_end)
        self.assertFalse(self.contract.contract_line_ids[1].date_end)
        self.assertEqual(self.contract.contract_line_ids[1].date_start, start_date)
        self.assertEqual(
            self.contract.contract_line_ids[1].product_id.id,
            self.new_tariff_product_id.id,
        )

    def test_wizard_tariff_change_with_future_date_start(self):
        tomorrow = date.today() + timedelta(days=1)
        self.contract.contract_line_ids[0].date_start = tomorrow
        self.contract._compute_current_tariff_contract_line()

        day_after_tomorrow = tomorrow + timedelta(days=1)

        wizard = (
            self.env["contract.tariff.change.wizard"]
            .with_context(active_id=self.contract.id)
            .with_user(self.user_admin)
            .create(
                {
                    "start_date": day_after_tomorrow,
                    "summary": "Tariff change 150 min 2 GB",
                }
            )
        )
        wizard.new_tariff_product_id = self.new_tariff_product_id

        wizard.button_change()

        self.assertFalse(self.contract.current_tariff_contract_line)
        self.assertEqual(
            self.contract.contract_line_ids[0].date_end,
            self.contract.contract_line_ids[0].date_start,
        )
        self.assertFalse(self.contract.contract_line_ids[1].date_end)
        self.assertEqual(
            self.contract.contract_line_ids[1].date_start, day_after_tomorrow
        )

    #    TODO: Review this test. When we create a new contract line, the
    #    existing contract lines end date is set to False. Why?
    #    def test_wizard_tariff_new_change_with_pending_change_in_future(self):
    #        """
    #        Tinc un contracte amb una linia il 20GB
    #        Demano un canvi a il 50 per a 1 de gener
    #        Demono un altre canvi per a il 5GB per al 1 de desembre
    #
    #        Com ha de quedar?
    #        1r wizard
    #        - La linia actual (il 20GB) ha de tenir la data de finalitzacio (31 de desembre).  # noqa
    #        - La linia nova (il 50GB) ha de tenir la data de inici (1 de gener).
    #        2n wizard
    #        - La linia actual (il 20GB) ha de tenir la data de finalitzacio (30 de novembre).  # noqa
    #        - La linia (il 50GB) es queda com està.
    #        - La linia nova (il 5GB) ha de tenir la data de inici (avui) i data de finalització (31 de desembre).  # noqa
    #        """
    #        current_cl = self.contract.contract_line_ids[0]
    #
    #        self.assertEqual(self.contract.current_tariff_contract_line, current_cl)
    #        self.assertFalse(current_cl.date_end)
    #
    #        another_product_mbl = self.browse_ref("somconnexio.TrucadesIllimitades50GB")  # noqa
    #        future_date = date.today() + timedelta(weeks=12)
    #
    #        # tariff change in future
    #        wizard = (
    #            self.env["contract.tariff.change.wizard"]
    #            .with_context(active_id=self.contract.id)
    #            .with_user(self.user_admin)
    #            .create(
    #                {
    #                    "start_date": future_date,
    #                    "summary": "Future tariff change",
    #                }
    #            )
    #        )
    #        wizard.new_tariff_product_id = another_product_mbl.id
    #        wizard.button_change()
    #
    #        future_cl = self.contract.contract_line_ids[1]
    #
    #        self.assertFalse(future_cl.date_end)
    #        # Date end of current tariff before future change
    #        self.assertEqual(current_cl.date_end, future_date - timedelta(days=1))
    #
    #        not_so_in_future_date = date.today() + timedelta(weeks=4)
    #
    #        # tariff change not so far in future
    #        wizard = (
    #            self.env["contract.tariff.change.wizard"]
    #            .with_context(active_id=self.contract.id)
    #            .with_user(self.user_admin)
    #            .create(
    #                {
    #                    "start_date": not_so_in_future_date,
    #                    "summary": "Not so in future tariff change",
    #                }
    #            )
    #        )
    #        wizard.new_tariff_product_id = self.new_tariff_product_id.id
    #        wizard.button_change()
    #
    #        not_so_in_future_cl = self.contract.contract_line_ids[2]
    #
    #        self.assertFalse(not_so_in_future_cl.date_end)
    #        self.assertEqual(future_cl.date_end, future_cl.date_start)
    #        # Date end of current tariff edited, before not so future change
    #        self.assertEqual(
    #            self.contract.current_tariff_contract_line.date_end,
    #            not_so_in_future_date - timedelta(days=1),
    #        )

    def test_ba_tariff_change(self):
        self.assertEqual(
            self.contract_ba.current_tariff_contract_line.product_id.id,
            self.ref("somconnexio.Fibra600Mb"),
        )
        start_date = date.today()
        wizard = (
            self.env["contract.tariff.change.wizard"]
            .with_context(
                active_id=self.contract_ba.id,
            )
            .create(
                {
                    "start_date": start_date,
                    "summary": "Tariff change Fibra 1Gb",
                }
            )
        )
        wizard.new_tariff_product_id = self.new_tariff_ba_same_tech_product_id
        partner_activities_before = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)]
        )

        wizard.button_change()
        partner_activities_after = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)],
        )
        self.assertEqual(
            len(partner_activities_after) - len(partner_activities_before), 1
        )
        created_activity = partner_activities_after[-1]
        self.assertEqual(
            created_activity.activity_type_id,
            self.browse_ref("somconnexio.mail_activity_type_tariff_change"),
        )
        self.assertEqual(created_activity.done, True)
        self.assertEqual(
            created_activity.summary,
            "Tariff change {}".format(
                self.new_tariff_ba_same_tech_product_id.showed_name
            ),
        )
        self.assertTrue(self.contract_ba.contract_line_ids[0].date_end)
        self.assertFalse(self.contract_ba.contract_line_ids[1].date_end)
        self.assertEqual(self.contract_ba.contract_line_ids[1].date_start, start_date)
        self.assertEqual(
            self.contract_ba.contract_line_ids[1].product_id.id,
            self.new_tariff_ba_same_tech_product_id.id,
        )

    def test_ba_tariff_diff_tech_change(self):
        self.assertEqual(
            self.contract_ba.current_tariff_contract_line.product_id.id,
            self.ref("somconnexio.Fibra600Mb"),
        )
        start_date = date.today()
        wizard = (
            self.env["contract.tariff.change.wizard"]
            .with_context(active_id=self.contract_ba.id, default_type="ba")
            .create(
                {
                    "start_date": start_date,
                    "summary": "Tariff change ADSL Sense Fix",
                }
            )
        )
        wizard.new_tariff_product_id = self.new_tariff_ba_different_tech_product_id
        self.assertRaises(ValidationError, wizard.button_change)
        self.assertEqual(self.contract_ba.contract_line_ids.product_id, self.product_ba)

    def test_ba_tariff_wo_fix_change(self):
        self.assertEqual(
            self.contract_ba.current_tariff_contract_line.product_id.id,
            self.ref("somconnexio.Fibra600Mb"),
        )
        start_date = date.today()
        wizard = (
            self.env["contract.tariff.change.wizard"]
            .with_context(active_id=self.contract_ba.id, default_type="ba")
            .create(
                {
                    "start_date": start_date,
                    "summary": "Tariff change Fibra 100Mb Sense Fix",
                }
            )
        )
        wizard.new_tariff_product_id = self.new_tariff_ba_wo_fix_product_id
        partner_activities_before = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)]
        )
        phone_number = self.contract_ba.phone_number
        wizard.button_change()
        partner_activities_after = self.env["mail.activity"].search(
            [("partner_id", "=", self.partner.id)],
        )
        self.assertEqual(
            len(partner_activities_after) - len(partner_activities_before), 1
        )
        created_activity = partner_activities_after[-1]
        self.assertEqual(
            created_activity.activity_type_id,
            self.browse_ref("somconnexio.mail_activity_type_tariff_change"),
        )
        self.assertEqual(created_activity.done, True)
        self.assertEqual(
            created_activity.summary,
            "Tariff change {}".format(self.new_tariff_ba_wo_fix_product_id.showed_name),
        )
        self.assertTrue(self.contract_ba.contract_line_ids[0].date_end)
        self.assertFalse(self.contract_ba.contract_line_ids[1].date_end)
        self.assertEqual(self.contract_ba.contract_line_ids[1].date_start, start_date)
        self.assertEqual(
            self.contract_ba.contract_line_ids[1].product_id.id,
            self.new_tariff_ba_wo_fix_product_id.id,
        )
        self.assertEqual(self.contract_ba.phone_number, phone_number)

    def test_wizard_tariff_change_KO_wo_start_date(self):
        wizard = (
            self.env["contract.tariff.change.wizard"]
            .with_context(active_id=self.contract.id)
            .with_user(self.user_admin)
            .create(
                {
                    "summary": "Tariff change 150 min 2 GB",
                }
            )
        )

        self.assertRaises(ValidationError, wizard.button_change)

    @patch("odoo.addons.mail.models.mail_thread.MailThread.message_post")
    def test_wizard_tariff_change_break_contract(self, mock_message_post):
        # Pack mobile and ba contracts
        self.contract.write(
            {
                "parent_pack_contract_id": self.contract_ba.id,
            }
        )
        self.contract.contract_line_ids[0].product_id = self.ref(
            "somconnexio.TrucadesIllimitades20GBPack"
        )
        self.contract_ba.write(
            {"children_pack_contract_ids": [(4, self.contract.id, 0)]}
        )

        self.assertTrue(self.contract.is_pack)
        self.assertTrue(self.contract_ba.is_pack)

        wizard = (
            self.env["contract.tariff.change.wizard"]
            .with_context(active_id=self.contract.id)
            .with_user(self.user_admin)
            .create(
                {
                    "start_date": date.today(),
                    "summary": "Tariff change 150 min 2 GB",
                }
            )
        )
        wizard.new_tariff_product_id = self.new_tariff_product_id

        wizard.button_change()

        self.assertFalse(self.contract.is_pack)
        self.assertFalse(self.contract_ba.is_pack)

        message = "Pack broken because of mobile tariff change. Old linked fiber contract ref: '{}'"  # noqa
        mock_message_post.assert_called_with(body=message.format(self.contract_ba.code))

    @patch(
        "odoo.addons.somconnexio.models.contract.Contract.quit_pack_and_update_mobile_tariffs",  # noqa
    )
    @patch("odoo.addons.mail.models.mail_thread.MailThread.message_post")
    def test_wizard_tariff_change_quit_sharing(self, mock_message_post, mock_quit_pack):
        contract = self.browse_ref("somconnexio.contract_mobile_il_50_shared_1_of_2")
        sharing_contract = self.browse_ref(
            "somconnexio.contract_mobile_il_50_shared_1_of_2"
        )
        self.assertTrue(contract.is_pack)
        original_shared_bond_id = contract.shared_bond_id
        self.assertTrue(original_shared_bond_id)
        self.assertEqual(sharing_contract.shared_bond_id, original_shared_bond_id)

        wizard = (
            self.env["contract.tariff.change.wizard"]
            .with_context(active_id=contract.id)
            .with_user(self.user_admin)
            .create(
                {
                    "start_date": date.today(),
                    "summary": "Tariff change 150 min 2 GB",
                }
            )
        )
        wizard.new_tariff_product_id = self.ref(
            "somconnexio.TrucadesIllimitades20GBPack"
        )
        wizard.button_change()

        message = "Stopped sharing data because of mobile tariff change. Old shared bond id: '{}'"  # noqa

        mock_message_post.assert_called_with(
            body=message.format(original_shared_bond_id)
        )
        # Sharing contract contract
        mock_quit_pack.assert_called_once_with()

    @patch("odoo.addons.mail.models.mail_thread.MailThread.message_post")
    def test_wizard_tariff_BA_change_do_not_break_contract(self, mock_message_post):
        # Pack mobile and ba contracts
        self.contract.write(
            {
                "parent_pack_contract_id": self.contract_ba.id,
            }
        )
        self.contract.contract_line_ids[0].product_id = self.ref(
            "somconnexio.TrucadesIllimitades20GBPack"
        )
        self.contract_ba.write(
            {"children_pack_contract_ids": [(4, self.contract.id, 0)]}
        )

        self.assertTrue(self.contract.is_pack)
        self.assertTrue(self.contract_ba.is_pack)

        wizard = (
            self.env["contract.tariff.change.wizard"]
            .with_context(active_id=self.contract_ba.id)
            .with_user(self.user_admin)
            .create(
                {
                    "start_date": date.today(),
                    "summary": "Tariff change Fiber without fix",
                }
            )
        )
        wizard.new_tariff_product_id = self.browse_ref("somconnexio.SenseFixFibra100Mb")

        wizard.button_change()

        self.assertTrue(self.contract.is_pack)
        self.assertTrue(self.contract_ba.is_pack)
