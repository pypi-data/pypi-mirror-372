from odoo.tests.common import TransactionCase
from unittest.mock import patch, Mock


class TestAgedPartnerBalanceXLSXReport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.report = self.env["report.a_f_r.report_aged_partner_balance_xlsx"]

    @patch(
        "odoo.addons.account_financial_report.report.aged_partner_balance_xlsx.AgedPartnerBalanceXslx._get_report_columns",  # noqa E501
        autospec=True,
    )
    def test_get_report_columns(self, mock_super):
        """
        Test that the _initialize_partner method adds the 'vat' and 'due_to_date' fields
        to the partner data.
        """
        base_columns = {
            0: {"field": "name"},
            1: {"field": "current"},
        }
        mock_super.return_value = base_columns

        self.assertEqual(len(base_columns), 2)

        report = Mock()
        report.show_move_line_details = False

        post_report_columns = self.report._get_report_columns(report)

        self.assertEqual(len(post_report_columns), 4)

        self.assertEqual(post_report_columns[0]["field"], "name")
        self.assertEqual(post_report_columns[1]["field"], "vat")
        self.assertEqual(post_report_columns[2]["field"], "current")
        self.assertEqual(post_report_columns[3]["field"], "due_to_date")
