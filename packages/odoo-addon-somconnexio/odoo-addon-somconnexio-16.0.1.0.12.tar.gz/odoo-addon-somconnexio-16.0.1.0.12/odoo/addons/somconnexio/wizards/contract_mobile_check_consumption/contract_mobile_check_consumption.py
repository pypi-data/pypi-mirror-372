from odoo import models, fields, api

from mm_proxy_python_client.resources.mobile_consumption import (
    MobileConsumption,
)
from datetime import date
from ...helpers.date import (
    first_day_this_month,
    date_to_str,
    last_day_of_month_of_given_date,
)


class MMBondConsumption(models.TransientModel):
    _name = "contract.mobile.check.consumption.mm.bond"

    name = fields.Char()
    phone_number = fields.Char()
    data_consumed = fields.Float()
    data_available = fields.Float()


class MMPTariffConsumption(MMBondConsumption):
    _name = "contract.mobile.check.consumption.mm.tariff"

    minutes_consumed = fields.Integer()
    minutes_available = fields.Integer()


class ContractMobileCheckConsumption(models.TransientModel):
    _name = "contract.mobile.check.consumption"
    _description = "Wizard to check mobile contract consumption"

    contract_id = fields.Many2one("contract.contract", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    mm_tariff_consumption_ids = fields.Many2many(
        comodel_name="contract.mobile.check.consumption.mm.tariff",
        relation="mm_tariff_consumption_check_consumption_wizard_table",
        string="Tariff",
        readonly=True,
    )
    mm_bond_consumption_ids = fields.Many2many(
        comodel_name="contract.mobile.check.consumption.mm.bond",
        relation="mm_bond_consumption_check_consumption_wizard_table",
        string="Bonds",
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults["contract_id"] = self.env.context["active_id"]
        defaults["start_date"] = first_day_this_month()
        defaults["end_date"] = date.today()
        return defaults

    @api.onchange("start_date")
    def onchange_start_date(self):
        self.end_date = last_day_of_month_of_given_date(self.start_date)

    def button_check(self):
        self.ensure_one()
        self.mm_tariff_consumption_ids = False
        self.mm_bond_consumption_ids = False

        if self.contract_id.contracts_in_pack:
            contracts_to_show = (
                self.contract_id.contracts_in_pack
                - self.contract_id.parent_pack_contract_id
            )
        else:
            contracts_to_show = self.contract_id

        get_consumption_params = {
            "start_date": date_to_str(self.start_date),
            "end_date": date_to_str(self.end_date),
        }

        for contract in contracts_to_show:
            get_consumption_params["phone_number"] = contract.phone_number

            consumption = MobileConsumption.get(**get_consumption_params)

            for tariff in consumption.tariffs:
                tariff_consumption = self.env[
                    "contract.mobile.check.consumption.mm.tariff"
                ].create(
                    {
                        "name": tariff.name,
                        "phone_number": contract.phone_number,
                        "minutes_consumed": tariff.minutes_consumed,
                        "minutes_available": (
                            tariff.minutes_available
                            if tariff.minutes_available != "ILIM"
                            else 43200  # minutes in 30 day month
                        ),
                        "data_consumed": self._MB_to_GB(tariff.data_consumed),
                        "data_available": self._MB_to_GB(tariff.data_available),
                    }
                )
                self.mm_tariff_consumption_ids += tariff_consumption
            for bond in consumption.bonds:
                bond_consumption = self.env[
                    "contract.mobile.check.consumption.mm.bond"
                ].create(
                    {
                        "name": bond.name,
                        "phone_number": contract.phone_number,
                        "data_consumed": self._MB_to_GB(bond.data_consumed),
                        "data_available": self._MB_to_GB(bond.data_available),
                    }
                )
                self.mm_bond_consumption_ids += bond_consumption

        # Do not quit the wizard view
        return {
            "type": "ir.actions.act_window",
            "res_model": "contract.mobile.check.consumption",
            "res_id": self.id,
            "view_mode": "form",
            "view_type": "form",
            "views": [(False, "form")],
            "target": "new",
        }

    def _MB_to_GB(self, mb):
        return int(mb) / 1024
