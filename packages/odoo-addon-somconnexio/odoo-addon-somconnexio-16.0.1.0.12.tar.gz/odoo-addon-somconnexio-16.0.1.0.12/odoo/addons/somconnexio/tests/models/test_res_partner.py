from mock import patch, call
from odoo.exceptions import UserError, ValidationError
from ..sc_test_case import SCTestCase


class TestResPartner(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.parent_partner = self.env["res.partner"].create(
            {
                "name": "test",
                "vat": "ES00470223B",
                "country_id": self.ref("base.es"),
            }
        )

    def test_contract_email_create(self):
        partner = self.env["res.partner"].create(
            {
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test",
                "city": "city",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "type": "contract-email",
            }
        )
        self.assertFalse(partner.name)
        self.assertFalse(partner.street)
        self.assertFalse(partner.street2)
        self.assertFalse(partner.city)
        self.assertFalse(partner.state_id)
        self.assertFalse(partner.country_id)
        self.assertEqual(partner.email, "test@example.com")
        self.assertEqual(partner.type, "contract-email")
        self.assertEqual(partner.parent_id, self.parent_partner)

    def test_contract_email_write_set_before(self):
        partner = self.env["res.partner"].create(
            {
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test",
                "city": "city",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
            }
        )
        partner.write({"type": "contract-email"})
        self.assertFalse(partner.name)
        self.assertFalse(partner.street)
        self.assertFalse(partner.street2)
        self.assertFalse(partner.city)
        self.assertFalse(partner.state_id)
        self.assertFalse(partner.country_id)
        self.assertEqual(partner.email, "test@example.com")
        self.assertEqual(partner.type, "contract-email")
        self.assertEqual(partner.parent_id, self.parent_partner)

    def test_contract_email_write_set_in(self):
        partner = self.env["res.partner"].create({})
        partner.write(
            {
                "type": "contract-email",
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test",
                "city": "city",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
            }
        )
        self.assertFalse(partner.name)
        self.assertFalse(partner.street)
        self.assertFalse(partner.street2)
        self.assertFalse(partner.city)
        self.assertFalse(partner.state_id)
        self.assertFalse(partner.country_id)
        self.assertEqual(partner.email, "test@example.com")
        self.assertEqual(partner.type, "contract-email")
        self.assertEqual(partner.parent_id, self.parent_partner)

    def test_not_contract_email_create(self):
        partner = self.env["res.partner"].create(
            {
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "type": "representative",
            }
        )
        self.assertEqual(partner.name, "test")
        self.assertEqual(partner.street, "test")
        self.assertEqual(partner.street2, "test2")
        self.assertEqual(partner.full_street, "test test2")
        self.assertEqual(partner.city, "test")
        self.assertEqual(partner.state_id, self.browse_ref("base.state_es_b"))
        self.assertEqual(partner.country_id, self.browse_ref("base.es"))
        self.assertEqual(partner.email, "test@example.com")
        self.assertEqual(partner.type, "representative")
        self.assertEqual(partner.parent_id, self.parent_partner)

    def test_error_invoice_partner_create(self):
        vals_partner = {
            "parent_id": self.parent_partner.id,
            "name": "test",
            "street": "test",
            "street2": "test2",
            "city": "test",
            "state_id": self.ref("base.state_es_b"),
            "country_id": self.ref("base.es"),
            "email": "test@example.com",
            "type": "invoice",
        }
        self.assertRaises(UserError, self.env["res.partner"].create, vals_partner)

    def test_not_contract_email_write_set_before(self):
        partner = self.env["res.partner"].create(
            {
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
            }
        )
        partner.write({"type": "representative"})
        self.assertEqual(partner.name, "test")
        self.assertEqual(partner.street, "test")
        self.assertEqual(partner.street2, "test2")
        self.assertEqual(partner.full_street, "test test2")
        self.assertEqual(partner.city, "test")
        self.assertEqual(partner.state_id, self.browse_ref("base.state_es_b"))
        self.assertEqual(partner.country_id, self.browse_ref("base.es"))
        self.assertEqual(partner.email, "test@example.com")
        self.assertEqual(partner.type, "representative")
        self.assertEqual(partner.parent_id, self.parent_partner)

    def test_not_contract_email_write_set_in(self):
        partner = self.env["res.partner"].create({})
        partner.write(
            {
                "type": "representative",
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
            }
        )
        self.assertEqual(partner.name, "test")
        self.assertEqual(partner.street, "test")
        self.assertEqual(partner.street2, "test2")
        self.assertEqual(partner.full_street, "test test2")
        self.assertEqual(partner.city, "test")
        self.assertEqual(partner.state_id, self.browse_ref("base.state_es_b"))
        self.assertEqual(partner.country_id, self.browse_ref("base.es"))
        self.assertEqual(partner.email, "test@example.com")
        self.assertEqual(partner.type, "representative")
        self.assertEqual(partner.parent_id, self.parent_partner)

    def test_sequence_without_ref_in_creation(self):
        partner_ref = self.browse_ref("somconnexio.sequence_partner").number_next_actual
        partner = self.env["res.partner"].create(
            {
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "type": "representative",
            }
        )
        self.assertEqual(str(partner_ref), partner.ref)

    def test_sequence_with_empty_ref_in_manual_UI_creation(self):
        partner_ref = self.browse_ref("somconnexio.sequence_partner").number_next_actual
        partner = self.env["res.partner"].create(
            {
                "ref": False,
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "type": "representative",
            }
        )
        self.assertEqual(str(partner_ref), partner.ref)

    def test_sequence_with_ref_in_creation(self):
        partner = self.env["res.partner"].create(
            {
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "type": "representative",
                "ref": "1234",
            }
        )
        self.assertEqual(partner.ref, "1234")

    def test_sequence_in_creation_with_parent_id(self):
        partner = self.env["res.partner"].create(
            {
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "type": "representative",
                "parent_id": 1,
            }
        )
        self.assertEqual(partner.ref, False)

    def test_name_search_contract_email(self):
        self.parent_partner.write(
            {
                "is_customer": True,
            }
        )
        partner = self.env["res.partner"].create({})
        partner.write(
            {
                "type": "contract-email",
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test",
                "city": "city",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
            }
        )
        name_search_results = self.env["res.partner"].name_search(
            args=[["is_customer", "=", True], ["parent_id", "=", False]],
            limit=8,
            name="test",
            operator="ilike",
        )
        self.assertEqual(len(name_search_results), 1)
        self.assertEqual(name_search_results[0][0], self.parent_partner.id)

    def test_create_normalize_vat(self):
        partner = self.env["res.partner"].create(
            {
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "type": "representative",
                "ref": "1234",
                "vat": "  44.589.589-H ",
            }
        )

        self.assertEqual(partner.vat, "44589589H")

    def test_write_normalize_vat(self):
        partner = self.env["res.partner"].create(
            {
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "type": "representative",
                "ref": "1234",
            }
        )
        partner.write(
            {
                "vat": "  44.589.589-H ",
            }
        )

        self.assertEqual(partner.vat, "44589589H")

    def test_has_active_contract(self):
        partner_id = self.parent_partner.id
        mobile_contract_service_info = self.env["mobile.service.contract.info"].create(
            {"phone_number": "654987654", "icc": "123"}
        )
        vals_contract = {
            "name": "Test Contract Mobile",
            "partner_id": partner_id,
            "invoice_partner_id": partner_id,
            "service_technology_id": self.ref("somconnexio.service_technology_mobile"),
            "service_supplier_id": self.ref("somconnexio.service_supplier_masmovil"),
            "mobile_contract_service_info_id": mobile_contract_service_info.id,
        }
        contract = self.env["contract.contract"].create(vals_contract)
        self.assertTrue(self.parent_partner.has_active_contract)

        contract.write({"is_terminated": True})

        self.assertFalse(self.parent_partner.has_active_contract)

    def test_does_not_have_active_contract(self):
        self.assertFalse(self.parent_partner.has_active_contract)

    def test_action_view_partner_invoices_only_filter_cancel(self):
        action = self.parent_partner.action_view_partner_invoices()
        domain = action["domain"]
        self.assertIn(("state", "not in", ["cancel"]), domain)

    @patch("odoo.addons.mail.models.mail_thread.MailThread.message_post")
    def test_address_one_field_changed_message_post(self, message_post_mock):
        partner = self.env["res.partner"].create(
            {
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "type": "representative",
            }
        )
        partner.write({"street": "test-new"})
        message_post_mock.assert_called_with(
            body="Contact address has been changed from test to test-new"
        )

    @patch("odoo.addons.mail.models.mail_thread.MailThread.message_post")
    def test_address_many_field_changed_message_post(self, message_post_mock):
        partner = self.env["res.partner"].create(
            {
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "type": "representative",
            }
        )
        partner.write({"street": "test-new", "street2": "test-new-2"})
        message_post_mock.assert_has_calls(
            [
                call(body="Contact address has been changed from test to test-new"),
                call(body="Contact address has been changed from test2 to test-new-2"),
            ],
            any_order=True,
        )

    @patch("odoo.addons.mail.models.mail_thread.MailThread.message_post")
    def test_address_other_fields_changed_message_post(self, message_post_mock):
        partner = self.env["res.partner"].create(
            {
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "type": "representative",
            }
        )
        partner.write({"name": "test-name"})
        message_post_mock.assert_not_called()

    @patch("odoo.addons.mail.models.mail_thread.MailThread.message_post")
    def test_address_mixed_fields_changed_message_post(self, message_post_mock):
        partner = self.env["res.partner"].create(
            {
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "type": "representative",
            }
        )
        partner.write({"name": "test-name", "street": "test-new"})
        message_post_mock.assert_called_once_with(
            body="Contact address has been changed from test to test-new"
        )

    @patch("odoo.addons.mail.models.mail_thread.MailThread.message_post")
    def test_address_state_id_changed_message_post(self, message_post_mock):
        partner = self.env["res.partner"].create(
            {
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "type": "representative",
            }
        )
        partner.write({"state_id": self.ref("base.state_es_m")})
        message_post_mock.assert_called_once_with(
            body="Contact address has been changed from Barcelona to Madrid"
        )

    @patch("odoo.addons.mail.models.mail_thread.MailThread.message_post")
    def test_address_country_id_changed_message_post(self, message_post_mock):
        partner = self.env["res.partner"].create(
            {
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "type": "representative",
            }
        )
        partner.write({"country_id": self.ref("base.fr")})
        message_post_mock.assert_called_once_with(
            body="Contact address has been changed from Spain to France"
        )

    def test_not_create_partner_if_vat_exists(self):
        partner_vals = {"name": "test", "vat": "ES39390704F"}
        self.env["res.partner"].create(partner_vals)
        self.assertRaisesRegex(
            UserError,
            "A partner with VAT {} already exists in our system".format(
                partner_vals["vat"]
            ),  # noqa
            self.env["res.partner"].create,
            partner_vals,
        )

    def test_not_update_partner_if_vat_exists(self):
        partner_vals = {"name": "test", "vat": "ES39390704F"}
        partner = self.env["res.partner"].create(partner_vals)

        partner_vals = {"vat": self.parent_partner.vat}

        self.assertRaisesRegex(
            ValidationError,
            "A partner with VAT {} already exists in our system".format(
                partner_vals["vat"]
            ),  # noqa
            partner.write,
            partner_vals,
        )

    def test_creation_with_bank_id(self):  # noqa
        partner_vals = {
            "parent_id": self.parent_partner.id,
            "name": "test",
            "street": "test",
            "street2": "test2",
            "city": "test",
            "state_id": self.ref("base.state_es_b"),
            "country_id": self.ref("base.es"),
            "email": "test@example.com",
            "type": "representative",
            "bank_ids": [(0, 0, {"acc_number": "ES9420805801101234567891"})],
        }
        self.assertTrue(self.env["res.partner"].create(partner_vals))

    def test_creation_raise_error_if_bank_inactive(self):  # noqa
        partner_vals = {
            "parent_id": self.parent_partner.id,
            "name": "test",
            "street": "test",
            "street2": "test2",
            "city": "test",
            "state_id": self.ref("base.state_es_b"),
            "country_id": self.ref("base.es"),
            "email": "test@example.com",
            "type": "representative",
            "bank_ids": [(0, 0, {"acc_number": "ES6621000418401234567891"})],
        }
        self.browse_ref("l10n_es_partner.res_bank_es_2100").write({"active": False})
        self.assertRaises(ValidationError, self.env["res.partner"].create, partner_vals)
        self.browse_ref("l10n_es_partner.res_bank_es_2100").write({"active": True})

    def test_creation_raise_error_if_bank_do_not_exist(self):  # noqa
        partner_vals = {
            "parent_id": self.parent_partner.id,
            "name": "test",
            "street": "test",
            "street2": "test2",
            "city": "test",
            "state_id": self.ref("base.state_es_b"),
            "country_id": self.ref("base.es"),
            "email": "test@example.com",
            "type": "representative",
            "bank_ids": [(0, 0, {"acc_number": "ES66999900418401234567891"})],
        }
        self.assertRaises(ValidationError, self.env["res.partner"].create, partner_vals)

    def test_creation_with_bank_id_assignation(self):  # noqa
        partner_bank = self.env["res.partner.bank"].create(
            {
                "acc_number": "ES9420805801101234567891",
                "partner_id": self.parent_partner.id,
            }
        )
        partner_vals = {
            "parent_id": self.parent_partner.id,
            "name": "test",
            "street": "test",
            "street2": "test2",
            "city": "test",
            "state_id": self.ref("base.state_es_b"),
            "country_id": self.ref("base.es"),
            "email": "test@example.com",
            "type": "representative",
            "bank_ids": [(4, partner_bank.id, 0)],
        }
        partner = self.env["res.partner"].create(partner_vals)
        self.assertEqual(partner.bank_ids.partner_id, partner)

    def test_edition_raise_error_if_bank_do_not_exist(self):  # noqa
        partner = self.env["res.partner"].create(
            {
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test",
                "city": "city",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
            }
        )
        self.assertRaises(
            ValidationError,
            partner.write,
            {"bank_ids": [(0, 0, {"acc_number": "ES66999900418401234567891"})]},
        )

    def test_edition_with_bank_ok(self):
        partner = self.env["res.partner"].create(
            {
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test",
                "city": "city",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
            }
        )
        self.assertTrue(
            partner.write(
                {"bank_ids": [(0, 0, {"acc_number": "ES1720852066623456789011"})]}
            )
        )

    def test_edition_with_bank_id_assignation(self):
        partner_bank = self.env["res.partner.bank"].create(
            {
                "acc_number": "ES9420805801101234567891",
                "partner_id": self.parent_partner.id,
            }
        )
        partner = self.env["res.partner"].create(
            {
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test",
                "city": "city",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
            }
        )
        self.assertTrue(partner.write({"bank_ids": [(6, 0, [partner_bank.id])]}))

    def test_edition_raise_error_if_bank_inactive(self):  # noqa
        partner = self.env["res.partner"].create(
            {
                "parent_id": self.parent_partner.id,
                "name": "test",
                "street": "test",
                "street2": "test2",
                "city": "test",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "type": "representative",
            }
        )
        self.browse_ref("l10n_es_partner.res_bank_es_2100").write({"active": False})
        self.assertRaises(
            ValidationError,
            partner.write,
            {"bank_ids": [(0, 0, {"acc_number": "ES6621000418401234567891"})]},
        )
        self.browse_ref("l10n_es_partner.res_bank_es_2100").write({"active": True})

    def test_get_mandate_ok(self):
        partner = self.env.ref("somconnexio.res_partner_2_demo")
        expected_mandate = self.env.ref("somconnexio.demo_mandate_partner_2_demo")
        partner_bank = partner.bank_ids[0]

        mandate = partner.get_mandate(partner_bank.sanitized_acc_number)
        self.assertEqual(mandate, expected_mandate)

    def test_get_mandate_not_found(self):
        partner = self.env.ref("somconnexio.res_partner_2_demo")
        new_iban = "ES0000000000000000000000"

        self.assertRaisesRegex(
            UserError,
            "Partner id %s without mandate with acc %s" % (partner.id, new_iban),
            partner.get_mandate,
            new_iban,
        )

    def test_get_or_create_contract_email_same(self):
        partner = self.env.ref("somconnexio.res_partner_2_demo")

        partner_email = partner.get_or_create_contract_email(partner.email)

        self.assertEqual(partner_email, partner)

    def test_get_or_create_contract_email_child(self):
        partner = self.env.ref("somconnexio.res_partner_2_demo")
        child_email = self.env["res.partner"].create(
            {
                "parent_id": partner.id,
                "name": "Child Partner",
                "email": "new.mail@test.coop",
                "type": "contract-email",
            }
        )
        partner_email = partner.get_or_create_contract_email(child_email.email)
        self.assertEqual(partner_email, child_email)

    def test_get_or_create_contract_email_new(self):
        partner = self.env.ref("somconnexio.res_partner_2_demo")
        new_email = "brand.new.mail@test.coop"

        partner_email = partner.get_or_create_contract_email(new_email)
        self.assertNotEqual(partner_email, partner)
        self.assertEqual(partner_email.email, new_email)
        self.assertEqual(partner_email.type, "contract-email")

    def test_get_or_create_contract_email_empty(self):
        partner = self.env.ref("somconnexio.res_partner_2_demo")

        partner_email = partner.get_or_create_contract_email(False)
        self.assertEqual(partner, partner_email)
