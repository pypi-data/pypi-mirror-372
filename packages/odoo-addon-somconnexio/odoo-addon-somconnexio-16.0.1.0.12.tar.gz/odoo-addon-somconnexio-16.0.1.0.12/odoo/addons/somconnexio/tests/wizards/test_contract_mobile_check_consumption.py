from datetime import date
from copy import deepcopy
from mock import patch, Mock
from ..sc_test_case import SCTestCase
from ...helpers.date import (
    first_day_this_month,
    last_day_of_month_of_given_date,
    date_to_str,
)
from mm_proxy_python_client.resources.mobile_consumption import (
    MobileConsumption,
)


class TestContractMobileCheckConsumption(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.mobile_contract = self.env.ref("somconnexio.contract_mobile_il_20")
        MobileConsumption = Mock(
            spec=["asset_id", "start_date", "end_date", "tariffs", "bonds"]
        )

        # MockTariff
        mock_tariff = Mock(
            spec=[
                "bond_id",
                "name",
                "data_consumed",
                "data_available",
                "minutes_consumed",
                "minutes_available",
            ]
        )
        mock_tariff.name = "LA MAGNIFICA 1"
        mock_tariff.bond_id = "T028"
        mock_tariff.data_consumed = "88"
        mock_tariff.data_available = "1024"
        mock_tariff.minutes_consumed = "34"
        mock_tariff.minutes_available = "ILIM"

        # MockBond
        mock_bond = Mock(
            spec=[
                "bond_id",
                "name",
                "data_consumed",
                "data_available",
            ]
        )
        mock_bond.name = "Bono adicional 500 MB"
        mock_bond.bond_id = "B102"
        mock_bond.data_consumed = "0"
        mock_bond.data_available = "512"

        self.mock_consumption = MobileConsumption()
        self.mock_consumption.asset_id = "12345"
        self.mock_consumption.tariffs = [mock_tariff]
        self.mock_consumption.bonds = [mock_bond]

    def test_check_consumption_default_values(self):
        wizard = (
            self.env["contract.mobile.check.consumption"]
            .with_context(active_id=self.mobile_contract.id)
            .create({})
        )

        self.assertEqual(wizard.contract_id, self.mobile_contract)
        self.assertEqual(wizard.start_date, first_day_this_month())
        self.assertEqual(wizard.end_date, date.today())
        self.assertFalse(wizard.mm_tariff_consumption_ids)
        self.assertFalse(wizard.mm_bond_consumption_ids)

    def test_check_consumption_onchange_start_date(self):
        wizard = (
            self.env["contract.mobile.check.consumption"]
            .with_context(active_id=self.mobile_contract.id)
            .create({})
        )
        wizard.start_date = date(2023, 9, 1)

        self.assertEqual(wizard.end_date, date.today())

        wizard.onchange_start_date()

        self.assertEqual(
            wizard.end_date, last_day_of_month_of_given_date(wizard.start_date)
        )

    @patch.object(MobileConsumption, "get")
    def test_check_consumption(self, mock_get):
        mock_get.return_value = self.mock_consumption

        wizard = (
            self.env["contract.mobile.check.consumption"]
            .with_context(active_id=self.mobile_contract.id)
            .create({})
        )

        wizard.button_check()

        self.assertEqual(len(wizard.mm_tariff_consumption_ids), 1)
        mm_tariff_item = wizard.mm_tariff_consumption_ids[0]
        tariff_mock_instance = self.mock_consumption.tariffs[0]

        self.assertEqual(mm_tariff_item.phone_number, self.mobile_contract.phone_number)
        self.assertEqual(mm_tariff_item.name, tariff_mock_instance.name)
        self.assertEqual(
            mm_tariff_item.minutes_consumed,
            int(tariff_mock_instance.minutes_consumed),
        )
        self.assertEqual(
            mm_tariff_item.minutes_available, 43200  # minutes in 30 day month
        )
        self.assertEqual(
            mm_tariff_item.data_consumed,
            int(tariff_mock_instance.data_consumed) / 1024,
        )
        self.assertEqual(
            mm_tariff_item.data_available,
            int(tariff_mock_instance.data_available) / 1024,
        )

        self.assertEqual(len(wizard.mm_bond_consumption_ids), 1)
        mm_bond_item = wizard.mm_bond_consumption_ids[0]
        bond_mock_instance = self.mock_consumption.bonds[0]

        self.assertEqual(mm_bond_item.phone_number, self.mobile_contract.phone_number)
        self.assertEqual(mm_bond_item.name, bond_mock_instance.name)
        self.assertEqual(
            mm_bond_item.data_consumed,
            int(bond_mock_instance.data_consumed) / 1024,
        )
        self.assertEqual(
            mm_bond_item.data_available,
            int(bond_mock_instance.data_available) / 1024,
        )

        mock_get.assert_called_once_with(
            phone_number=self.mobile_contract.phone_number,
            start_date=date_to_str(wizard.start_date),
            end_date=date_to_str(wizard.end_date),
        )

    @patch.object(MobileConsumption, "get")
    def test_check_consumption_sharing(self, mock_get):
        sharing_contract = self.env.ref(
            "somconnexio.contract_mobile_il_50_shared_1_of_2"
        )
        sharing_contract._compute_contracts_in_pack()
        other_sharing_contract = (
            sharing_contract.contracts_in_pack
            - sharing_contract
            - sharing_contract.parent_pack_contract_id
        )

        mock_consumption_1 = deepcopy(self.mock_consumption)
        mock_consumption_1.tariffs[0].name = "Tarifa Ilimitada Compartida"
        mock_consumption_1.tariffs[0].data_available = "0"
        mock_consumption_1.tariffs[0].data_consumed = "0"

        mock_consumption_1.bonds[
            0
        ].name = "Bono Compartido 50GB_3P Cablemovil_Community"
        mock_consumption_1.bonds[0].data_available = "51200"
        mock_consumption_1.bonds[0].data_consumed = "3245"

        mock_consumption_2 = deepcopy(mock_consumption_1)
        mock_consumption_2.bonds[0].data_consumed = "8282"

        def side_effect_mock_get(start_date, end_date, phone_number):
            if phone_number == sharing_contract.phone_number:
                return mock_consumption_1
            elif phone_number == other_sharing_contract.phone_number:
                return mock_consumption_2

        mock_get.side_effect = side_effect_mock_get

        wizard = (
            self.env["contract.mobile.check.consumption"]
            .with_context(active_id=sharing_contract.id)
            .create({})
        )
        wizard.button_check()

        self.assertEqual(len(wizard.mm_tariff_consumption_ids), 2)
        self.assertEqual(
            wizard.mm_tariff_consumption_ids[0].name, "Tarifa Ilimitada Compartida"
        )
        self.assertEqual(len(wizard.mm_bond_consumption_ids), 2)

        mm_bond_data_consumptions = wizard.mm_bond_consumption_ids.mapped(
            "data_consumed"
        )
        self.assertIn(
            int(mock_consumption_1.bonds[0].data_consumed) / 1024,
            mm_bond_data_consumptions,
        )
        self.assertIn(
            int(mock_consumption_2.bonds[0].data_consumed) / 1024,
            mm_bond_data_consumptions,
        )
