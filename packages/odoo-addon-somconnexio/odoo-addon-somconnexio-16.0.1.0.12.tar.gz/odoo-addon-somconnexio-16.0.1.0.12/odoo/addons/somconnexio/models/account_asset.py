from odoo import models, api


class AccountAsset(models.Model):
    _inherit = ["account.asset", "mail.thread"]
    _name = "account.asset"

    @api.model
    def _xls_active_fields(self):
        """
        Update list in custom module to add/drop columns or change order
        """
        return [
            "account",
            "name",
            "code",
            "date_start",
            "date_end",
            "depreciation_base",
            "salvage_value",
            "period_start_value",
            "period_depr",
            "period_end_value",
            "period_end_depr",
            "method",
            "method_number",
            "perc_amort_anual",
            "prorata",
            "state",
        ]
