from datetime import date, timedelta

from ..sc_test_case import SCTestCase


class TestContractHolderChangeWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.partner = self.browse_ref("somconnexio.res_partner_1_demo")
        self.partner_b = self.browse_ref("somconnexio.res_partner_2_demo")
        self.banking_mandate = self.browse_ref(
            "somconnexio.demo_mandate_partner_2_demo"
        )
        self.new_contract_domain = [
            ("partner_id", "=", self.partner_b.id),
            ("create_reason", "=", "holder_change"),
        ]

        self.fiber_contract = self.browse_ref("somconnexio.contract_fibra_600")
        self.mobile_contract = self.browse_ref("somconnexio.contract_mobile_il_20")

        group_can_terminate_contract = self.env.ref("contract.can_terminate_contract")
        group_can_terminate_contract.users |= self.env.user

    def test_wizard_holder_change_ok(self):
        wizard = (
            self.env["contract.holder.change.wizard"]
            .with_context(active_id=self.fiber_contract.id)
            .create(
                {
                    "change_date": date.today(),
                    "partner_id": self.partner_b.id,
                    "banking_mandate_id": self.banking_mandate.id,
                    "change_all_contracts_from_pack": "no",
                }
            )
        )

        self.assertFalse(wizard.is_pack)
        self.assertEqual(
            wizard.payment_mode,
            self.browse_ref("somconnexio.payment_mode_inbound_sepa"),
        )
        self.assertEqual(
            wizard.available_banking_mandates,
            self.env["account.banking.mandate"].browse(self.banking_mandate.id),
        )
        new_service_partner_b = self.env["res.partner"].search(
            [
                ("parent_id", "=", self.partner_b.id),
                ("type", "=", "service"),
                ("street", "=", self.partner.street),
            ]
        )

        self.assertFalse(new_service_partner_b)

        wizard.button_change()

        self.assertEqual(
            self.fiber_contract.terminate_reason_id,
            self.browse_ref("somconnexio.reason_holder_change"),
        )
        self.assertEqual(
            self.fiber_contract.terminate_user_reason_id,
            self.browse_ref("somconnexio.user_reason_other"),
        )
        self.assertTrue(self.fiber_contract.is_terminated)

        new_contract = self.env["contract.contract"].search(self.new_contract_domain)

        self.assertEqual(
            self.fiber_contract.service_supplier_id, new_contract.service_supplier_id
        )
        self.assertEqual(
            self.fiber_contract.service_technology_id,
            new_contract.service_technology_id,
        )
        self.assertNotEqual(
            self.fiber_contract.mm_fiber_service_contract_info_id,
            new_contract.mm_fiber_service_contract_info_id,
        )
        self.assertEqual(
            self.fiber_contract.contract_line_ids[0].date_end, date.today()
        )
        self.assertEqual(
            new_contract.contract_line_ids[0].date_start,
            date.today() + timedelta(days=1),
        )
        self.assertEqual(new_contract.mandate_id, self.banking_mandate)

        new_service_partner_b = self.env["res.partner"].search(
            [
                ("parent_id", "=", self.partner_b.id),
                ("type", "=", "service"),
                ("street", "=", self.partner.street),
            ]
        )
        self.assertTrue(new_service_partner_b)
        self.assertEqual(new_contract.service_partner_id.id, new_service_partner_b.id)
        self.assertEqual(
            new_contract.crm_lead_line_id.lead_id.name, "Change Holder process"
        )
        self.assertEqual(
            new_contract.crm_lead_line_id.lead_id.partner_id, self.partner_b
        )
        self.assertEqual(
            new_contract.crm_lead_line_id.lead_id.stage_id,
            self.env.ref("crm.stage_lead4"),
        )
        self.assertEqual(new_contract.create_reason, "holder_change")

    def test_wizard_holder_change_ok_mobile(self):
        wizard = (
            self.env["contract.holder.change.wizard"]
            .with_context(active_id=self.mobile_contract.id)
            .create(
                {
                    "change_date": date.today(),
                    "partner_id": self.partner_b.id,
                    "banking_mandate_id": self.banking_mandate.id,
                }
            )
        )
        wizard.button_change()

        self.new_contract_domain.append(
            ("phone_number", "=", self.mobile_contract.phone_number)
        )
        new_contract = self.env["contract.contract"].search(self.new_contract_domain)

        self.assertFalse(wizard.is_pack)
        self.assertTrue(wizard.is_mobile)
        self.assertEqual(
            new_contract.crm_lead_line_id.lead_id.name, "Change Holder process"
        )
        self.assertEqual(
            new_contract.crm_lead_line_id.lead_id.partner_id, self.partner_b
        )
        self.assertEqual(
            new_contract.crm_lead_line_id.lead_id.stage_id,
            self.env.ref("crm.stage_lead4"),
        )
        self.assertEqual(new_contract.create_reason, "holder_change")

    def test_wizard_holder_change_service_address_already_existed(self):
        same_service_partner_b = self.env["res.partner"].create(
            {
                "parent_id": self.partner_b.id,
                "type": "service",
                "street": self.fiber_contract.service_partner_id.street,
            }
        )
        other_service_partner_b = self.env["res.partner"].create(
            {
                "parent_id": self.partner_b.id,
                "type": "service",
                "street": "Partner b diferent street",
            }
        )

        wizard = (
            self.env["contract.holder.change.wizard"]
            .with_context(active_id=self.fiber_contract.id)
            .create(
                {
                    "change_date": date.today(),
                    "partner_id": self.partner_b.id,
                    "banking_mandate_id": self.banking_mandate.id,
                }
            )
        )
        wizard.button_change()

        self.new_contract_domain.append(
            ("phone_number", "=", self.fiber_contract.phone_number)
        )
        new_contract = self.env["contract.contract"].search(self.new_contract_domain)

        self.assertEqual(new_contract.service_partner_id.id, same_service_partner_b.id)
        self.assertNotEqual(
            new_contract.service_partner_id.id, other_service_partner_b.id
        )

    def test_wizard_holder_skip_oneshot(self):
        contract_line = {
            "name": "Hola",
            "product_id": self.browse_ref("somconnexio.RecollidaRouter").id,
            "date_start": "2020-01-01",
        }
        self.fiber_contract.write({"contract_line_ids": [(0, 0, contract_line)]})

        wizard = (
            self.env["contract.holder.change.wizard"]
            .with_context(active_id=self.fiber_contract.id)
            .create(
                {
                    "change_date": date.today(),
                    "partner_id": self.partner_b.id,
                    "banking_mandate_id": self.banking_mandate.id,
                }
            )
        )
        wizard.button_change()

        self.new_contract_domain.append(
            ("phone_number", "=", self.fiber_contract.phone_number)
        )
        new_contract = self.env["contract.contract"].search(self.new_contract_domain)

        self.assertTrue(
            self.fiber_contract.contract_line_ids.filtered(
                lambda l: l.product_id == self.browse_ref("somconnexio.RecollidaRouter")
            )
        )
        self.assertTrue(new_contract.contract_line_ids)
        self.assertFalse(
            new_contract.contract_line_ids.filtered(
                lambda l: l.product_id == self.browse_ref("somconnexio.RecollidaRouter")
            )
        )

    def test_wizard_holder_skip_terminated_line(self):
        contract_line = {
            "name": "Hola",
            "product_id": self.browse_ref("somconnexio.Fibra600Mb").id,
            "date_start": "2020-01-01",
            "date_end": "2020-01-15",
        }
        self.fiber_contract.write({"contract_line_ids": [(0, 0, contract_line)]})

        wizard = (
            self.env["contract.holder.change.wizard"]
            .with_context(active_id=self.fiber_contract.id)
            .create(
                {
                    "change_date": date.today(),
                    "partner_id": self.partner_b.id,
                    "banking_mandate_id": self.banking_mandate.id,
                }
            )
        )
        wizard.button_change()

        self.new_contract_domain.append(
            ("phone_number", "=", self.fiber_contract.phone_number)
        )
        new_contract = self.env["contract.contract"].search(self.new_contract_domain)

        self.assertTrue(
            self.fiber_contract.contract_line_ids.filtered(lambda l: l.date_end)
        )
        self.assertTrue(new_contract.contract_line_ids)
        self.assertFalse(new_contract.contract_line_ids.filtered(lambda l: l.date_end))

    def test_wizard_holder_only_fiber_in_pack(self):
        fiber_contract_pack = self.browse_ref(
            "somconnexio.contract_fibra_600_pack"
        )  # noqa
        fiber_product = fiber_contract_pack.current_tariff_product

        wizard = (
            self.env["contract.holder.change.wizard"]
            .with_context(active_id=fiber_contract_pack.id)
            .create(
                {
                    "change_date": date.today() - timedelta(days=1),
                    "partner_id": self.partner_b.id,
                    "change_all_contracts_from_pack": "no",
                    "banking_mandate_id": self.banking_mandate.id,
                }
            )
        )
        wizard.button_change()

        self.assertTrue(wizard.is_pack)
        self.assertEqual(
            fiber_contract_pack.terminate_reason_id,
            self.browse_ref("somconnexio.reason_holder_change"),
        )
        self.assertEqual(
            fiber_contract_pack.terminate_user_reason_id,
            self.browse_ref("somconnexio.user_reason_other"),
        )
        self.assertTrue(fiber_contract_pack.is_terminated)

        self.new_contract_domain.append(
            ("phone_number", "=", fiber_contract_pack.phone_number)
        )
        new_contract = self.env["contract.contract"].search(self.new_contract_domain)

        self.assertEqual(new_contract.current_tariff_product, fiber_product)
        self.assertFalse(new_contract.is_terminated)

    def test_wizard_holder_only_mobile_in_pack(self):
        mbl_contract_pack = self.browse_ref("somconnexio.contract_mobile_il_20_pack")
        new_product_mobile = self.browse_ref("somconnexio.TrucadesIllimitades5GB")

        wizard = (
            self.env["contract.holder.change.wizard"]
            .with_context(active_id=mbl_contract_pack.id)
            .create(
                {
                    "change_date": date.today() - timedelta(days=1),
                    "partner_id": self.partner_b.id,
                    "change_all_contracts_from_pack": "no",
                    "banking_mandate_id": self.banking_mandate.id,
                    "product_id": new_product_mobile.id,
                }
            )
        )
        wizard.button_change()

        self.assertTrue(wizard.is_pack)
        self.assertEqual(
            mbl_contract_pack.terminate_reason_id,
            self.browse_ref("somconnexio.reason_holder_change"),
        )
        self.assertEqual(
            mbl_contract_pack.terminate_user_reason_id,
            self.browse_ref("somconnexio.user_reason_other"),
        )
        self.assertTrue(mbl_contract_pack.is_terminated)

        self.new_contract_domain.append(
            ("phone_number", "=", mbl_contract_pack.phone_number)
        )
        new_contract = self.env["contract.contract"].search(self.new_contract_domain)

        self.assertEqual(new_contract.current_tariff_product, new_product_mobile)
        self.assertFalse(new_contract.is_terminated)

    def test_wizard_holder_whole_pack(self):
        fiber_contract_pack = self.browse_ref("somconnexio.contract_fibra_300_shared")
        mbl_contract_pack_1 = self.browse_ref(
            "somconnexio.contract_mobile_il_50_shared_1_of_3"
        )
        fiber_product = fiber_contract_pack.current_tariff_product
        mbl_product = mbl_contract_pack_1.current_tariff_product

        wizard = (
            self.env["contract.holder.change.wizard"]
            .with_context(active_id=fiber_contract_pack.id)
            .create(
                {
                    "change_date": date.today() - timedelta(days=1),
                    "partner_id": self.partner_b.id,
                    "change_all_contracts_from_pack": "yes",
                    "banking_mandate_id": self.banking_mandate.id,
                }
            )
        )
        wizard.button_change()

        self.assertTrue(wizard.is_pack)
        self.assertTrue(
            all(
                contract.is_terminated
                for contract in wizard.contract_id.contracts_in_pack
            )
        )

        self.assertEqual(
            fiber_contract_pack.terminate_reason_id,
            self.browse_ref("somconnexio.reason_holder_change_pack"),
        )
        self.assertEqual(
            fiber_contract_pack.terminate_user_reason_id,
            self.browse_ref("somconnexio.user_reason_other"),
        )

        new_pack_contracts = self.env["contract.contract"].search(
            [
                ("partner_id", "=", self.partner_b.id),
                (
                    "phone_number",
                    "in",
                    wizard.contract_id.contracts_in_pack.mapped("phone_number"),
                ),
            ]
        )

        self.assertEqual(
            len(new_pack_contracts), len(wizard.contract_id.contracts_in_pack)
        )

        new_fiber_contract = new_pack_contracts.filtered("is_fiber")
        new_mobile_contracts = new_pack_contracts.filtered("is_mobile")

        self.assertEqual(new_fiber_contract.current_tariff_product, fiber_product)
        self.assertEqual(new_mobile_contracts[0].current_tariff_product, mbl_product)
        self.assertEqual(
            new_fiber_contract.children_pack_contract_ids, new_mobile_contracts
        )
