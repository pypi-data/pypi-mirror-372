from ..sc_test_case import SCTestCase


class TestResPartnerBankTest(SCTestCase):
    def test_fill_bank_id_on_create(self):
        new_iban = "ES1720852066623456789011"
        partner_id = self.browse_ref("somconnexio.res_partner_2_demo")

        partner_bank = self.env["res.partner.bank"].create(
            {"acc_type": "iban", "acc_number": new_iban, "partner_id": partner_id.id}
        )

        self.assertEqual(partner_bank.bank_id.name, "Ibercaja Banco")
