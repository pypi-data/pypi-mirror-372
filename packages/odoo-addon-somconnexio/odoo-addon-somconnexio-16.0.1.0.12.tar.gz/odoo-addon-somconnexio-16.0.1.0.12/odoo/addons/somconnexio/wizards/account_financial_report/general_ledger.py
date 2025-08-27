from odoo import models, fields, api


class GeneralLedgerWizard(models.TransientModel):
    _inherit = "general.ledger.report.wizard"
    general_expenses = fields.Boolean()

    @api.onchange("receivable_accounts_only", "payable_accounts_only", "general_expenses") # noqa
    def onchange_type_accounts_only(self):
        general_expenses_accounts = [
            62300001,
            62300002,
            62300010,
            62300005,
            62300006,
            62100000,
            62900000,
            62800000,
            64900000,
            62300000,
            62900010,
            62600000,
            62500000,
            62700000,
            62700001,
            69100000,
            62800002,
            62800001,
            62300003,
            62300004,
            62300007,
            62300008,
            62900003,
            62900002,
            62400000,
            62900001,
            60200040,
            60200000,
            63100000,
            60200020,
            60200030,
            67800001,
            62300009,
            62300011,
        ]
        # Handle receivable/payable accounts only change
        if self.receivable_accounts_only or self.payable_accounts_only:
            domain = [("company_id", "=", self.company_id.id)]
            if self.receivable_accounts_only and self.payable_accounts_only:
                domain += [
                    ("account_type", "in", ("asset_receivable", "liability_payable"))
                ]
            elif self.receivable_accounts_only:
                domain += [("account_type", "=", "asset_receivable")]
            elif self.payable_accounts_only:
                domain += [("account_type", "=", "liability_payable")]
            if self.general_expenses:
                domain += [('code', 'in', general_expenses_accounts)]
            self.account_ids = self.env["account.account"].search(domain)
        else:
            if self.general_expenses:
                self.account_ids = self.env["account.account"].search(
                    [
                        ("company_id", "=", self.company_id.id),
                        ("code", "in", general_expenses_accounts),
                    ]
                )
            else:
                self.account_ids = None
