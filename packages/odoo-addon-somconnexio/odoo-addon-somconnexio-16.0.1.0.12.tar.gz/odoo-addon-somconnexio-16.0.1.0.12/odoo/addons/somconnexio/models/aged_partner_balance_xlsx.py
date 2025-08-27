from odoo import models, _
from collections import OrderedDict


class AgedPartnerBalanceXslx(models.AbstractModel):
    _inherit = "report.a_f_r.report_aged_partner_balance_xlsx"
    _description = "Aged Partner Balance Report with VAT"

    def _VAT_report_column(self):
        """
        Column data for partner's VAT as report column.
        """
        return {
            "header": _("VAT"),
            "field": "vat",
            "field_footer_total": "vat",
            "type": "string",
            "width": 14,
        }

    def _due_to_date_report_column(self):
        """
        Column data for due_to_date as report column.
        """
        return {
            "header": _("Due to date"),
            "field": "due_to_date",
            "field_footer_total": "due_to_date",
            "field_footer_percent": "percent_due_to_date",
            "type": "amount",
            "width": 14,
        }

    def _get_report_columns(self, report):
        """
        Get report columns from original method and add the a new column
        for partner's VAT, after the `name` field.
        """
        columns = super()._get_report_columns(report)
        if not report.show_move_line_details:
            new_columns = OrderedDict()
            vat_inserted = False
            due_inserted = False
            for i in sorted(columns.keys()):
                col = columns[i]
                new_columns[len(new_columns)] = col
                if not vat_inserted and col.get("field") == "name":
                    new_columns[len(new_columns)] = self._VAT_report_column()
                    vat_inserted = True
                if not due_inserted and col.get("field") == "current":
                    new_columns[len(new_columns)] = self._due_to_date_report_column()
                    due_inserted = True
            return new_columns

        return columns
