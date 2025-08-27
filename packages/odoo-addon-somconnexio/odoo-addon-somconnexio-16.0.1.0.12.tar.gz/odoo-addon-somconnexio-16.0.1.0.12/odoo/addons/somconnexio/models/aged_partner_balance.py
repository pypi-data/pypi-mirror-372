from odoo import models, api


class AgedPartnerBalanceReport(models.AbstractModel):
    _description = "Aged Partner Balance Report SomConnexio"
    _inherit = "report.account_financial_report.aged_partner_balance"

    @api.model
    def _initialize_partner(self, ag_pb_data, acc_id, prt_id):
        """
        Initialize the `vat` and `due_to_date` field for each partner.
        """
        ag_pb_data = super()._initialize_partner(ag_pb_data, acc_id, prt_id)
        ag_pb_data[acc_id][prt_id]["vat"] = ""
        ag_pb_data[acc_id][prt_id]["due_to_date"] = 0.0
        return ag_pb_data

    @api.model
    def _initialize_account(self, ag_pb_data, acc_id):
        """
        Initialize the `vat` and `due_to_date` field for each account.
        """
        ag_pb_data = super()._initialize_account(ag_pb_data, acc_id)
        ag_pb_data[acc_id]["vat"] = ""
        ag_pb_data[acc_id]["due_to_date"] = 0.0
        return ag_pb_data

    @api.model
    def _calculate_amounts(
        self, ag_pb_data, acc_id, prt_id, residual, due_date, date_at_object
    ):
        """
        Add `due_to_date` field to the `ag_pb_data` dictionary for each account
        and partner.
        """
        ag_pb_data = super()._calculate_amounts(
            ag_pb_data, acc_id, prt_id, residual, due_date, date_at_object
        )

        if due_date and due_date < date_at_object:
            ag_pb_data[acc_id]["due_to_date"] += residual
            ag_pb_data[acc_id][prt_id]["due_to_date"] += residual

        return ag_pb_data

    @api.model
    def _calculate_percent(self, aged_partner_data):
        """
        Calculate the percentage of the amount due to date for each account.
        TODO: Show cummul and percentage to views
        """
        aged_partner_data = super()._calculate_percent(aged_partner_data)
        for account in aged_partner_data:
            if abs(account["residual"]) > 0.01:
                total = account["residual"]
                account.update(
                    {
                        "percent_due_to_date": abs(
                            round((account["due_to_date"] / total) * 100, 2)
                        ),
                    }
                )
            else:
                account.update(
                    {
                        "percent_due_to_date": 0.0,
                    }
                )
        return aged_partner_data

    def _create_account_list(
        self,
        ag_pb_data,
        accounts_data,
        partners_data,
        journals_data,
        show_move_line_details,
        date_at_oject,
    ):
        """
        Add `vat` and `due_to_date` fields within partners
        from `aged_partner_data`
        """

        aged_partner_data = super()._create_account_list(
            ag_pb_data,
            accounts_data,
            partners_data,
            journals_data,
            show_move_line_details,
            date_at_oject,
        )

        for account in aged_partner_data:
            acc_id = account["id"]
            partner_index = 0
            for prt_id in ag_pb_data[acc_id]:
                # Only id in dict is a partner id key
                if isinstance(prt_id, int):
                    partner = self.env["res.partner"].browse(prt_id)
                    vat = partner.vat
                    account["partners"][partner_index]["vat"] = vat
                    account["partners"][partner_index]["due_to_date"] = ag_pb_data[
                        acc_id
                    ][prt_id]["due_to_date"]
                    account["due_to_date"] = ag_pb_data[acc_id]["due_to_date"]
                    partner_index += 1
        return aged_partner_data
