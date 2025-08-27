from odoo.exceptions import UserError, ValidationError

from datetime import timedelta, date

from ..helper_service import (
    contract_fiber_create_data,
    contract_adsl_create_data,
    contract_mobile_create_data,
    contract_4g_create_data,
    random_icc,
)
from ..sc_test_case import SCComponentTestCase


class TestContract(SCComponentTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.Contract = self.env["contract.contract"]
        self.partner = self.browse_ref("somconnexio.res_partner_2_demo")
        self.service_partner = self.env["res.partner"].create(
            {"parent_id": self.partner.id, "name": "Service partner", "type": "service"}
        )
        self.router_4g_contract_data = contract_4g_create_data(self.env, self.partner)
        self.adsl_contract_data = contract_adsl_create_data(self.env, self.partner)
        self.fiber_contract_data = contract_fiber_create_data(self.env, self.partner)
        self.mobile_contract_data = contract_mobile_create_data(self.env, self.partner)
        self.adsl_contract_service_info = self.env["adsl.service.contract.info"].browse(
            self.adsl_contract_data["adsl_service_contract_info_id"]
        )
        self.router_product = self.adsl_contract_service_info.router_product_id
        # self.router_lot = self.adsl_contract_service_info.router_lot_id
        self.vodafone_fiber_contract_service_info = self.env[
            "vodafone.fiber.service.contract.info"
        ].browse(self.fiber_contract_data["vodafone_fiber_service_contract_info_id"])
        self.mobile_contract_service_info = self.env[
            "mobile.service.contract.info"
        ].browse(self.mobile_contract_data["mobile_contract_service_info_id"])

    def test_service_contact_wrong_type(self, *args):
        partner_id = self.partner.id
        service_partner = self.env["res.partner"].create(
            {"parent_id": partner_id, "name": "Partner not service"}
        )
        vals_contract = self.adsl_contract_data
        vals_contract["service_partner_id"] = service_partner.id
        self.assertRaises(ValidationError, self.Contract.create, (vals_contract,))

    def test_service_contact_right_type(self, *args):
        self.assertTrue(self.Contract.create(self.fiber_contract_data))

    def test_contact_without_code(self, *args):
        contract_code = self.browse_ref(
            "somconnexio.sequence_contract"
        ).number_next_actual
        contract = self.Contract.create(self.fiber_contract_data)

        self.assertEqual(contract.code, str(contract_code))

    def test_contact_with_empty_code_manual_UI_creation(self, *args):
        vals_contract = self.fiber_contract_data
        vals_contract["code"] = False
        contract_code = self.browse_ref(
            "somconnexio.sequence_contract"
        ).number_next_actual
        contract = self.Contract.create(vals_contract)

        self.assertEqual(contract.code, str(contract_code))

    def test_contact_with_code(self, *args):
        vals_contract = self.fiber_contract_data
        vals_contract["code"] = 1234
        contract = self.Contract.create(vals_contract)
        self.assertEqual(contract.code, "1234")

    def test_service_contact_wrong_parent(self, *args):
        service_partner = self.env["res.partner"].create(
            {
                "parent_id": self.ref("somconnexio.res_partner_1_demo"),
                "name": "Partner wrong parent",
                "type": "service",
            }
        )
        vals_contract = self.fiber_contract_data
        vals_contract["service_partner_id"] = service_partner.id
        self.assertRaises(ValidationError, self.Contract.create, (vals_contract,))

    def test_email_not_partner_not_child_wrong_type(self, *args):
        wrong_email = self.env["res.partner"].create(
            {"name": "Bad email", "email": "hello@example.com"}
        )
        vals_contract = self.mobile_contract_data
        vals_contract["email_ids"] = [(6, 0, [wrong_email.id])]

        self.assertRaises(ValidationError, self.Contract.create, (vals_contract,))

    def test_email_not_partner_not_child_right_type(self, *args):
        wrong_email = self.env["res.partner"].create(
            {
                "name": "Bad email",
                "email": "hello@example.com",
                "type": "contract-email",
            }
        )
        vals_contract = self.mobile_contract_data
        vals_contract["email_ids"] = [(6, 0, [wrong_email.id])]

        self.assertRaises(ValidationError, self.Contract.create, (vals_contract,))

    def test_email_same_partner_not_contract_email_type(self, *args):
        vals_contract = self.mobile_contract_data
        vals_contract["email_ids"] = [(6, 0, [self.partner.id])]
        self.assertTrue(self.Contract.create(vals_contract))

    def test_email_child_partner_wrong_type(self, *args):
        child_email = self.env["res.partner"].create(
            {
                "name": "Bad email",
                "email": "hello@example.com",
                "parent_id": self.partner.id,
                "type": "delivery",
            }
        )
        vals_contract = self.mobile_contract_data
        vals_contract["email_ids"] = [(6, 0, [child_email.id])]

        self.assertRaises(ValidationError, self.Contract.create, (vals_contract,))

    def test_email_child_partner_right_type(self, *args):
        partner_id = self.partner.id
        child_email = self.env["res.partner"].create(
            {
                "name": "Right email",
                "email": "hello@example.com",
                "parent_id": partner_id,
                "type": "contract-email",
            }
        )
        vals_contract = self.mobile_contract_data
        vals_contract["email_ids"] = [(6, 0, [child_email.id])]

        self.assertTrue(self.Contract.create(vals_contract))

    def test_sequence_in_creation(self, *args):
        contract_code = self.browse_ref(
            "somconnexio.sequence_contract"
        ).number_next_actual
        contract = self.Contract.create(self.mobile_contract_data)

        self.assertEqual(contract.code, str(contract_code))

    def test_set_previous_id_vodafone(self, *args):
        vals_contract = self.fiber_contract_data
        contract = self.Contract.create(vals_contract)
        contract.previous_id = "vf123"

        self.assertEqual(self.vodafone_fiber_contract_service_info.previous_id, "vf123")

    def test_set_vodafone_id_in_submodel(self, *args):
        vals_contract = self.fiber_contract_data
        contract = self.Contract.create(vals_contract)
        self.vodafone_fiber_contract_service_info.vodafone_id = "vf123"

        self.assertEqual(contract.vodafone_id, "vf123")

    def test_set_vodafone_offer_code_in_submodel(self, *args):
        vals_contract = self.fiber_contract_data
        contract = self.Contract.create(vals_contract)
        self.vodafone_fiber_contract_service_info.vodafone_offer_code = "vf123"

        self.assertEqual(contract.vodafone_offer_code, "vf123")

    def test_set_previous_id_and_name_and_icc_router_4G(self, *args):
        vals_contract = self.router_4g_contract_data
        contract = self.Contract.create(vals_contract)

        self.assertFalse(contract.previous_id)
        self.assertEqual(contract.icc, contract.router_4G_service_contract_info_id.icc)

        expected_previous_id = "vf123"
        expected_icc = random_icc(self.env)

        contract.previous_id = expected_previous_id
        contract.icc = expected_icc
        self.assertEqual(
            contract.router_4G_service_contract_info_id.previous_id,
            expected_previous_id,
        )
        self.assertEqual(
            contract.router_4G_service_contract_info_id.icc,
            expected_icc,
        )
        self.assertEqual(contract.name, "-")

    def test_set_previous_id_masmovil(self, *args):
        expected_previous_id = "mm123"
        contract = self.Contract.create(
            contract_fiber_create_data(self.env, self.partner, provider="masmovil")
        )
        contract.previous_id = expected_previous_id

        self.assertEqual(
            contract.mm_fiber_service_contract_info_id.previous_id, expected_previous_id
        )

    def test_set_previous_id_adsl(self, *args):
        expected_previous_id = "adsl123"
        vals_contract = self.adsl_contract_data
        contract = self.Contract.create(vals_contract)
        contract.previous_id = expected_previous_id

        self.assertEqual(
            contract.adsl_service_contract_info_id.previous_id, expected_previous_id
        )

    def test_set_previous_id_xoln(self, *args):
        expected_previous_id = "xoln123"
        contract = self.Contract.create(
            contract_fiber_create_data(self.env, self.partner, provider="xoln")
        )
        contract.previous_id = expected_previous_id

        self.assertEqual(
            contract.xoln_fiber_service_contract_info_id.previous_id,
            expected_previous_id,
        )

    def test_set_icc_mobile(self, *args):
        expected_icc = random_icc(self.env)
        contract = self.Contract.create(self.mobile_contract_data)
        self.assertNotEqual(contract.icc, expected_icc)
        contract.icc = expected_icc

        self.assertEqual(contract.mobile_contract_service_info_id.icc, expected_icc)

    def adsl_contract_service_info_wo_phone_number(self, *args):
        adsl_contract_service_info = self.env["adsl.service.contract.info"].create(
            {
                "administrative_number": "123",
                "router_product_id": self.router_product.id,
                # "router_lot_id": self.router_lot.id,
                "ppp_user": "ringo",
                "ppp_password": "rango",
                "endpoint_user": "user",
                "endpoint_password": "password",
            }
        )
        self.assertEqual(adsl_contract_service_info.phone_number, "-")

    def test_children_pack_contract_ids(self, *args):
        fiber_vals_contract = self.fiber_contract_data
        parent_contract = self.Contract.create(fiber_vals_contract)
        mobile_vals_contract = self.mobile_contract_data
        mobile_vals_contract["parent_pack_contract_id"] = parent_contract.id
        contract = self.Contract.create(mobile_vals_contract)
        self.assertEqual(contract.parent_pack_contract_id, parent_contract)
        self.assertEqual(parent_contract.children_pack_contract_ids, contract)
        self.assertEqual(parent_contract.number_contracts_in_pack, 2)
        self.assertTrue(contract.is_pack)
        self.assertTrue(parent_contract.is_pack)

    def test_compute_contracts_in_pack(self, *args):
        ba_vals_contract = contract_fiber_create_data(self.env, self.partner)
        fiber_contract = self.Contract.create(ba_vals_contract)

        mbl_vals_contract = contract_mobile_create_data(self.env, self.partner)
        mbl_vals_contract["parent_pack_contract_id"] = fiber_contract.id
        mbl_1_contract = self.Contract.create(mbl_vals_contract)

        self.assertEqual(fiber_contract.children_pack_contract_ids, mbl_1_contract)
        self.assertEqual(fiber_contract.number_contracts_in_pack, 2)

        # Create second mobile contract linked to same fiber
        mbl_2_contract = self.Contract.create(mbl_vals_contract)

        self.assertTrue(mbl_2_contract.contracts_in_pack)
        self.assertEqual(
            set(mbl_2_contract.contracts_in_pack.ids),
            set([mbl_1_contract.id, mbl_2_contract.id, fiber_contract.id]),
        )
        self.assertEqual(
            set(fiber_contract.children_pack_contract_ids.ids),
            set([mbl_1_contract.id, mbl_2_contract.id]),
        )
        self.assertEqual(fiber_contract.number_contracts_in_pack, 3)

        # Create third mobile contract linked to same fiber
        mbl_3_contract = self.Contract.create(mbl_vals_contract)

        self.assertTrue(mbl_3_contract.contracts_in_pack)
        self.assertEqual(len(mbl_3_contract.contracts_in_pack), 4)
        self.assertEqual(
            set(mbl_3_contract.contracts_in_pack.ids),
            set(
                [
                    mbl_1_contract.id,
                    mbl_2_contract.id,
                    mbl_3_contract.id,
                    fiber_contract.id,
                ]
            ),
        )
        self.assertEqual(
            set(fiber_contract.children_pack_contract_ids.ids),
            set([mbl_1_contract.id, mbl_2_contract.id, mbl_3_contract.id]),
        )
        self.assertEqual(fiber_contract.number_contracts_in_pack, 4)

    def test_not_pack_contract_id(self, *args):
        contract = self.Contract.create(self.fiber_contract_data)
        self.assertFalse(contract.parent_pack_contract_id)
        self.assertEqual(contract.number_contracts_in_pack, 0)
        self.assertFalse(contract.is_pack)

    def test_break_contracts_in_pack(self, *args):
        parent_contract = self.env.ref("somconnexio.contract_fibra_600_pack")
        contract = self.env.ref("somconnexio.contract_mobile_il_20_pack")

        self.assertTrue(parent_contract.is_pack)
        self.assertTrue(contract.is_pack)

        parent_contract.terminate_date = date.today() - timedelta(days=2)
        parent_contract.break_packs()

        self.assertFalse(parent_contract.is_pack)
        self.assertFalse(contract.is_pack)

    def test_break_contract_sharing_data_from_2_to_1(self, *args):
        """
        Contract 1 from 2 sharing contract terminates,
        breaking the sharing bond pack, so the other
        looses the shared bond id.
        """

        contract = self.env.ref("somconnexio.contract_mobile_il_50_shared_1_of_2")
        contract._compute_contracts_in_pack()
        sharing_contract = self.env.ref(
            "somconnexio.contract_mobile_il_50_shared_2_of_2"
        )

        self.assertTrue(contract.is_pack)
        self.assertTrue(contract.shared_bond_id)

        # Terminate contract
        terminate_date = date.today() - timedelta(days=2)
        contract.write(
            {
                "date_end": terminate_date,
                "terminate_date": terminate_date,
                "is_terminated": True,
            }
        )
        contract.break_packs()

        self.assertFalse(contract.is_pack)
        self.assertFalse(contract.shared_bond_id)
        self.assertFalse(sharing_contract.shared_bond_id)

    def test_break_contract_sharing_data_from_3_to_2(self, *args):
        """
        Contract 1 from 3 sharing contract terminates,
        quitting the pack, so the other two need to change their tariff.
        """

        contract = self.browse_ref("somconnexio.contract_mobile_il_50_shared_1_of_3")
        contract._compute_contracts_in_pack()
        sharing_contract_1 = self.browse_ref(
            "somconnexio.contract_mobile_il_50_shared_2_of_3"
        )
        sharing_contract_2 = self.browse_ref(
            "somconnexio.contract_mobile_il_50_shared_3_of_3"
        )

        self.assertTrue(contract.is_pack and contract.shared_bond_id)
        self.assertIn(contract, sharing_contract_1.contracts_in_pack)
        self.assertEqual(len(sharing_contract_1.contracts_in_pack), 4)
        self.assertEqual(
            sharing_contract_1.current_tariff_product,
            self.browse_ref("somconnexio.50GBCompartides3mobils"),
        )
        self.assertEqual(
            sharing_contract_1.contracts_in_pack,
            sharing_contract_2.contracts_in_pack,
        )
        self.assertEqual(
            sharing_contract_1.current_tariff_product,
            sharing_contract_2.current_tariff_product,
        )

        # Terminate contract
        terminate_date = date.today() - timedelta(days=2)
        contract.write(
            {
                "date_end": terminate_date,
                "terminate_date": terminate_date,
                "is_terminated": True,
            }
        )

        contract.break_packs()

        # TODO -> This was not necessary with ODOO12
        sharing_contract_1._compute_contracts_in_pack()
        sharing_contract_2._compute_contracts_in_pack()
        sharing_contract_1._compute_current_tariff_contract_line()
        sharing_contract_2._compute_current_tariff_contract_line()

        self.assertFalse(contract.is_pack and contract.shared_bond_id)
        self.assertNotIn(contract, sharing_contract_1.contracts_in_pack)
        self.assertEqual(len(sharing_contract_1.contracts_in_pack), 3)
        self.assertEqual(
            sharing_contract_1.current_tariff_product,
            self.browse_ref("somconnexio.50GBCompartides2mobils"),
        )
        self.assertEqual(
            sharing_contract_1.current_tariff_start_date, contract.terminate_date
        )
        self.assertEqual(
            sharing_contract_1.contracts_in_pack,
            sharing_contract_2.contracts_in_pack,
        )
        self.assertEqual(
            sharing_contract_1.current_tariff_product,
            sharing_contract_2.current_tariff_product,
        )

    def test_quit_pack_and_update_mobile_tariffs_from_2_to_1(self, *args):
        """
        Contract 1 from 2 sharing contract changes its tariff,
        quitting the pack, so both of them loose their shared_bond_id.
        """

        contract = self.env.ref("somconnexio.contract_mobile_il_50_shared_1_of_2")
        contract._compute_contracts_in_pack()
        sharing_contract = self.env.ref(
            "somconnexio.contract_mobile_il_50_shared_2_of_2"
        )

        self.assertTrue(contract.is_pack)
        self.assertTrue(contract.shared_bond_id)

        # Tariff change out of pack
        new_tariff_product_id = self.env.ref("somconnexio.TrucadesIllimitades20GB")
        today = date.today()
        new_tariff_line_dct = {
            "name": new_tariff_product_id.name,
            "product_id": new_tariff_product_id.id,
            "date_start": today,
        }
        contract.write(
            {
                "contract_line_ids": [
                    (0, 0, new_tariff_line_dct),
                    (
                        1,
                        contract.current_tariff_contract_line.id,
                        {"date_end": today - timedelta(days=1)},
                    ),
                ]
            }
        )

        contract.quit_pack_and_update_mobile_tariffs()

        self.assertFalse(contract.shared_bond_id)
        self.assertFalse(sharing_contract.shared_bond_id)

    def test_quit_pack_and_update_mobile_tariffs_from_3_to_2(self, *args):
        """
        Contract 1 from 3 sharing contract changes its tariff,
        quitting the pack, so the it looses its shared_bond_id.
        """

        contract = self.browse_ref("somconnexio.contract_mobile_il_50_shared_1_of_3")
        contract._compute_contracts_in_pack()
        sharing_contract_1 = self.browse_ref(
            "somconnexio.contract_mobile_il_50_shared_2_of_3"
        )
        sharing_contract_2 = self.browse_ref(
            "somconnexio.contract_mobile_il_50_shared_3_of_3"
        )

        self.assertTrue(contract.is_pack and contract.shared_bond_id)
        self.assertEqual(len(sharing_contract_1.contracts_in_pack), 4)
        self.assertEqual(
            sharing_contract_1.current_tariff_product,
            self.browse_ref("somconnexio.50GBCompartides3mobils"),
        )

        # Tariff change out of pack
        new_tariff_product_id = self.env.ref("somconnexio.TrucadesIllimitades20GB")
        today = date.today()
        new_tariff_line_dct = {
            "name": new_tariff_product_id.name,
            "product_id": new_tariff_product_id.id,
            "date_start": today,
        }
        contract.write(
            {
                "contract_line_ids": [
                    (0, 0, new_tariff_line_dct),
                    (
                        1,
                        contract.current_tariff_contract_line.id,
                        {"date_end": today - timedelta(days=1)},
                    ),
                ]
            }
        )
        contract.quit_pack_and_update_mobile_tariffs()

        # TODO -> This was not necessary with ODOO12
        sharing_contract_1._compute_contracts_in_pack()
        sharing_contract_2._compute_contracts_in_pack()
        sharing_contract_1._compute_current_tariff_contract_line()
        sharing_contract_2._compute_current_tariff_contract_line()

        self.assertFalse(contract.is_pack and contract.shared_bond_id)
        self.assertNotIn(contract, sharing_contract_1.contracts_in_pack)
        self.assertEqual(len(sharing_contract_1.contracts_in_pack), 3)
        self.assertEqual(
            sharing_contract_1.current_tariff_product,
            self.browse_ref("somconnexio.50GBCompartides2mobils"),
        )
        self.assertEqual(sharing_contract_1.current_tariff_start_date, today)
        self.assertEqual(
            sharing_contract_1.contracts_in_pack,
            sharing_contract_2.contracts_in_pack,
        )
        self.assertEqual(
            sharing_contract_1.current_tariff_product,
            sharing_contract_2.current_tariff_product,
        )

    def test_update_pack_mobiles_tariffs_after_joining_pack(self, *args):
        sharing_contract_1 = self.env.ref(
            "somconnexio.contract_mobile_il_50_shared_1_of_2"
        )
        sharing_contract_2 = self.env.ref(
            "somconnexio.contract_mobile_il_50_shared_2_of_2"
        )
        sharing_data_product_mobile_2 = self.env.ref(
            "somconnexio.50GBCompartides2mobils"
        )
        sharing_data_product_mobile_3 = self.env.ref(
            "somconnexio.50GBCompartides3mobils"
        )

        mbl_vals_contract = contract_mobile_create_data(
            self.env, sharing_contract_1.partner_id
        )
        new_mbl_contract = self.Contract.create(mbl_vals_contract)
        sharing_contract_line_data = {
            "name": "Sharing 3 product contract_line",
            "product_id": sharing_data_product_mobile_3.id,
            "date_start": "2020-01-01",
        }
        parent_contract = sharing_contract_1.parent_pack_contract_id
        new_mbl_contract.write(
            {
                "parent_pack_contract_id": parent_contract.id,
                "contract_line_ids": [(0, 0, sharing_contract_line_data)],
            }
        )
        new_mbl_contract.mobile_contract_service_info_id.shared_bond_id = (
            sharing_contract_1.shared_bond_id
        )

        self.assertEqual(
            sharing_contract_1.current_tariff_product, sharing_data_product_mobile_2
        )
        self.assertEqual(
            sharing_contract_2.current_tariff_product, sharing_data_product_mobile_2
        )

        new_mbl_contract.update_pack_mobiles_tariffs_after_joining_pack()

        # TODO -> This was not necessary with ODOO12
        sharing_contract_1._compute_current_tariff_contract_line()
        sharing_contract_2._compute_current_tariff_contract_line()

        # Check that sharing contracts have been updated with 3rd pack contract
        self.assertEqual(
            new_mbl_contract.current_tariff_product, sharing_data_product_mobile_3
        )
        self.assertEqual(len(new_mbl_contract.contracts_in_pack), 4)
        self.assertIn(
            sharing_contract_1,
            new_mbl_contract.contracts_in_pack,
        )
        self.assertIn(
            sharing_contract_2,
            new_mbl_contract.contracts_in_pack,
        )
        self.assertEqual(new_mbl_contract.parent_pack_contract_id, parent_contract)
        self.assertEqual(
            sharing_contract_1.current_tariff_product, sharing_data_product_mobile_3
        )
        self.assertEqual(
            sharing_contract_2.current_tariff_product, sharing_data_product_mobile_3
        )

    def test_update_pack_mobiles_tariffs_after_joining_pack_extra(self, *args):
        sharing_contract_3 = self.env.ref(
            "somconnexio.contract_mobile_il_50_shared_3_of_3"
        )
        sharing_data_product_mobile_3 = self.env.ref(
            "somconnexio.50GBCompartides3mobils"
        )

        self.assertEqual(
            sharing_contract_3.current_tariff_product, sharing_data_product_mobile_3
        )
        self.assertEqual(len(sharing_contract_3.contracts_in_pack), 4)
        mbl_vals_contract = contract_mobile_create_data(
            self.env, sharing_contract_3.partner_id
        )
        new_mbl_contract = self.Contract.create(mbl_vals_contract)
        sharing_contract_line_data = {
            "name": "Sharing 3 product contract_line",
            "product_id": sharing_data_product_mobile_3.id,
            "date_start": "2020-01-01",
        }
        parent_contract = sharing_contract_3.parent_pack_contract_id
        new_mbl_contract.write(
            {
                "parent_pack_contract_id": parent_contract.id,
                "contract_line_ids": [(0, 0, sharing_contract_line_data)],
            }
        )
        new_mbl_contract.mobile_contract_service_info_id.shared_bond_id = (
            sharing_contract_3.shared_bond_id
        )
        self.assertRaisesRegex(
            UserError,
            "No more than 3 mobiles can be packed together",
            new_mbl_contract.update_pack_mobiles_tariffs_after_joining_pack,
        )

    def test_display_name_broadband_contracts(self, *args):
        contract = self.browse_ref("somconnexio.contract_fibra_600")

        expected_name = "{} - {}, {}, {}, {}".format(
            contract.name,
            contract.service_partner_id.full_street,
            contract.service_partner_id.city,
            contract.service_partner_id.zip,
            contract.service_partner_id.state_id.name,
        )
        self.assertEqual(contract.display_name, expected_name)

    def test_active_started_not_ended(self):
        """Line with start < today, no end → active True"""
        contract = self.env.ref("somconnexio.contract_mobile_il_20")
        line = contract.contract_line_ids[0]

        self.assertTrue(line.date_start < date.today())
        self.assertFalse(line.date_end)
        self.assertTrue(
            contract._is_contract_line_active(line),
        )

    def test_active_started_not_ended_yet(self):
        """Line with start < today < end → active True"""
        contract = self.env.ref("somconnexio.contract_mobile_il_20")
        line = contract.contract_line_ids[0]
        line.write(
            {
                "date_end": date.today() + timedelta(days=10),
            }
        )

        self.assertTrue(line.date_start < date.today())
        self.assertTrue(line.date_end > date.today())
        self.assertTrue(
            contract._is_contract_line_active(line),
        )

    def test_not_active_before_start(self):
        """Line with start > today → active False"""
        contract = self.env.ref("somconnexio.contract_mobile_il_20")
        line = contract.contract_line_ids[0]

        line.write(
            {
                "date_start": date.today() + timedelta(days=1),
                "date_end": False,
            }
        )
        self.assertFalse(line.date_start < date.today())
        self.assertFalse(line.date_end)
        self.assertFalse(
            contract._is_contract_line_active(line),
        )

    def test_not_active_after_end(self):
        """Line with start < end < today → active False"""
        contract = self.env.ref("somconnexio.contract_mobile_il_20")
        line = contract.contract_line_ids[0]
        line.write(
            {
                "date_end": date.today() - timedelta(days=1),
            }
        )
        self.assertTrue(line.date_start < date.today())
        self.assertTrue(line.date_end)
        self.assertFalse(
            contract._is_contract_line_active(line),
        )

    def test_not_active_if_canceled(self):
        """Line with start < today, canceled → active False"""
        contract = self.env.ref("somconnexio.contract_mobile_il_20")
        line = contract.contract_line_ids[0]
        line.write(
            {
                "is_canceled": True,
                "date_end": False,
            }
        )

        self.assertTrue(line.date_start < date.today())
        self.assertFalse(line.date_end)
        self.assertFalse(
            contract._is_contract_line_active(line),
        )
