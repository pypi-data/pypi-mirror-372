from odoo.tests.common import TransactionCase
from unittest.mock import patch
from datetime import date


class TestAgedPartnerBalanceReport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.report = self.env["report.account_financial_report.aged_partner_balance"]

    @patch(
        "odoo.addons.account_financial_report.report.aged_partner_balance.AgedPartnerBalanceReport._initialize_partner",  # noqa E501
        autospec=True,
    )
    def test_initialize_partner_adds_fields(self, mock_super):
        """
        Test that the _initialize_partner method adds the 'vat' and 'due_to_date' fields
        to the partner data.
        """
        pre_init_data = {1: {10: {}}}
        mock_super.return_value = pre_init_data
        post_init_data = self.report._initialize_partner(pre_init_data, 1, 10)
        self.assertIn("vat", post_init_data[1][10])
        self.assertIn("due_to_date", post_init_data[1][10])
        self.assertEqual(post_init_data[1][10]["vat"], "")
        self.assertEqual(post_init_data[1][10]["due_to_date"], 0.0)

    @patch(
        "odoo.addons.account_financial_report.report.aged_partner_balance.AgedPartnerBalanceReport._initialize_account",  # noqa E501
        autospec=True,
    )
    def test_initialize_account_adds_fields(self, mock_super):
        """
        Test that the _initialize_account method adds the 'vat' and 'due_to_date' fields
        to the account data.
        """
        pre_init_data = {1: {}}
        mock_super.return_value = pre_init_data
        post_init_data = self.report._initialize_account(pre_init_data, 1)
        self.assertEqual(post_init_data[1]["vat"], "")
        self.assertEqual(post_init_data[1]["due_to_date"], 0.0)

    @patch(
        "odoo.addons.account_financial_report.report.aged_partner_balance.AgedPartnerBalanceReport._calculate_amounts",  # noqa E501
        autospec=True,
    )
    def test_calculate_amounts_due_to_date_added(self, mock_super):
        """
        Test that the _calculate_amounts method adds the 'due_to_date' field
        to the account and partner data when the due date is before the date at.
        """
        acc_id = (1,)
        prt_id = 10
        residual = 100.0
        date_at = date(2024, 1, 2)
        due_date = date(2024, 1, 1)
        pre_ag_pb_data = {acc_id: {prt_id: {"due_to_date": 0.0}, "due_to_date": 0.0}}
        mock_super.return_value = pre_ag_pb_data

        post_ag_pb_data = self.report._calculate_amounts(
            pre_ag_pb_data, acc_id, prt_id, residual, due_date, date_at
        )
        self.assertEqual(post_ag_pb_data[acc_id]["due_to_date"], residual)
        self.assertEqual(post_ag_pb_data[acc_id][prt_id]["due_to_date"], residual)

    @patch(
        "odoo.addons.account_financial_report.report.aged_partner_balance.AgedPartnerBalanceReport._calculate_percent",  # noqa E501
        autospec=True,
    )
    def test_calculate_percent_sets_value(self, mock_super):
        """
        Test that the _calculate_percent method sets the 'percent_due_to_date' field
        to the correct value based on the 'due_to_date' and 'residual' fields.
        """
        pre_aged_partner_data = [{"residual": 200.0, "due_to_date": 50.0}]
        mock_super.return_value = pre_aged_partner_data
        post_aged_partner_data = self.report._calculate_percent(pre_aged_partner_data)
        self.assertEqual(post_aged_partner_data[0]["percent_due_to_date"], 25.0)

    @patch(
        "odoo.addons.account_financial_report.report.aged_partner_balance.AgedPartnerBalanceReport._create_account_list",  # noqa E501
        autospec=True,
    )
    def test_create_account_list_sets_vat_and_due(self, mock_super):
        partner = self.env.ref("somconnexio.res_partner_1_demo")
        date_at = date.today()
        ag_pb_data = {
            1: {
                partner.id: {"due_to_date": 123.45},
                "due_to_date": 123.45,
            }
        }
        accounts_data = {1: {"id": 1}}
        partners_data = {partner.id: {"id": partner.id}}
        pre_aged_partner_data = [{"id": 1, "partners": [{}]}]

        mock_super.return_value = pre_aged_partner_data
        post_aged_partner_data = self.report._create_account_list(
            ag_pb_data, accounts_data, partners_data, {}, False, date_at
        )
        self.assertEqual(post_aged_partner_data[0]["partners"][0]["vat"], partner.vat)
        self.assertEqual(
            post_aged_partner_data[0]["partners"][0]["due_to_date"], 123.45
        )
        self.assertEqual(post_aged_partner_data[0]["due_to_date"], 123.45)
