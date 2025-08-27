from mock import patch
from odoo.exceptions import ValidationError

from ..helper_service import crm_lead_create, random_icc
from ..sc_test_case import SCTestCase


class CRMLeadTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.partner_id = self.env.ref("somconnexio.res_partner_2_demo")
        self.partner_iban = self.partner_id.bank_ids[0].sanitized_acc_number

        self.crm_lead = crm_lead_create(self.env, self.partner_id, "mobile")
        self.crm_lead_mobile = self.crm_lead.lead_line_ids[
            0
        ].mobile_isp_info.phone_number
        self.product_pack_mobile = self.env.ref(
            "somconnexio.TrucadesIllimitades20GBPack"
        )
        self.product_mobile = self.env.ref("somconnexio.TrucadesIllimitades20GB")
        self.product_pack_fiber = self.env.ref("somconnexio.Fibra100Mb")
        self.mobile_isp_info = self.env["mobile.isp.info"].create(
            {"type": "new", "icc": random_icc(self.env), "phone_number": "616382488"}
        )
        self.mobile_lead_line_vals = {
            "name": "TEST",
            "product_id": self.product_mobile.id,
            "mobile_isp_info": self.mobile_isp_info.id,
            "iban": self.partner_iban,
        }

        self.CRMLeadLine = self.env["crm.lead.line"]

    def test_crm_lead_action_set_won(self):
        self.crm_lead.write(
            {
                "stage_id": self.env.ref("crm.stage_lead3").id,
            }
        )

        self.crm_lead.action_set_won()
        self.assertEqual(self.crm_lead.stage_id, self.env.ref("crm.stage_lead4"))

    def test_crm_lead_action_set_won_raise_error_if_not_in_remesa_stage(self):
        self.assertNotEqual(self.crm_lead.stage_id, self.env.ref("crm.stage_lead3"))
        self.assertRaisesRegex(
            ValidationError,
            "The crm lead must be in remesa or delivery generated stage.",
            self.crm_lead.action_set_won,
        )

    def test_crm_lead_action_set_remesa_raise_error_if_not_in_new_stage(self):
        self.crm_lead.write(
            {
                "stage_id": self.env.ref("somconnexio.stage_lead5").id,
            }
        )
        self.assertNotEqual(self.crm_lead.stage_id, self.env.ref("crm.stage_lead1"))
        self.assertRaisesRegex(
            ValidationError,
            "The crm lead must be in new stage.",
            self.crm_lead.action_set_remesa,
        )

    def test_crm_lead_action_set_cancelled(self):
        self.crm_lead.write(
            {
                "stage_id": self.env.ref("somconnexio.stage_lead5").id,
            }
        )
        self.crm_lead.action_set_cancelled()
        self.assertEqual(
            self.crm_lead.stage_id, self.env.ref("somconnexio.stage_lead5")
        )

    @patch("odoo.addons.mail.models.mail_template.MailTemplate.send_mail")
    def test_crm_lead_action_send_email(self, mock_send_mail):
        crm_lead = crm_lead_create(self.env, self.partner_id, "pack", portability=True)
        self.assertFalse(crm_lead.email_sent)

        crm_lead.action_send_email()

        self.assertTrue(crm_lead.email_sent)
        mock_send_mail.assert_called_with(crm_lead.id)
        template = self.env.ref("somconnexio.crm_lead_creation_manual_email_template")
        self.assertFalse(template.attachment_ids)

    def test_ensure_crm_lead_iban_in_partner(self):
        self.crm_lead.write(
            {
                "stage_id": self.env.ref("crm.stage_lead3").id,
            }
        )
        new_iban = "ES9000246912501234567891"
        self.crm_lead.lead_line_ids[0].iban = new_iban

        self.assertNotIn(
            new_iban, self.partner_id.bank_ids.mapped("sanitized_acc_number")
        )

        self.crm_lead.action_set_won()

        self.assertEqual(len(self.partner_id.bank_ids), 2)
        self.assertIn(new_iban, self.partner_id.bank_ids.mapped("sanitized_acc_number"))

    def test_crm_lead_partner_email(self):
        self.assertEqual(self.crm_lead.email_from, self.partner_id.email)

    def test_crm_lead_new_email(self):
        new_email = "new.email@demo.net"
        self.crm_lead.write(
            {
                "email_from": new_email,
            }
        )
        self.assertEqual(self.crm_lead.email_from, new_email)

    def test_crm_lead_action_set_remesa(self):
        self.crm_lead.action_set_remesa()
        self.assertEqual(self.crm_lead.stage_id, self.env.ref("crm.stage_lead3"))

    def test_crm_lead_action_set_remesa_raise_error_with_invalid_bank(self):
        fake_iban = "ES99999999999999999999999"

        self.crm_lead.lead_line_ids[0].iban = fake_iban

        self.assertRaisesRegex(
            ValidationError,
            "Error in {}: Invalid bank.".format(fake_iban),
            self.crm_lead.action_set_remesa,
        )

    def test_crm_lead_action_set_remesa_raise_error_with_existent_phone_number(self):
        self.crm_lead.write(
            {
                "stage_id": self.env.ref("crm.stage_lead4").id,
            }
        )
        crm_lead = crm_lead_create(self.env, self.partner_id, "mobile")

        # Same phone number from self.crm_lead
        crm_lead.lead_line_ids[0].mobile_isp_info.write(
            {
                "phone_number": self.crm_lead_mobile,
            }
        )

        self.assertRaisesRegex(
            ValidationError,
            "Error in {}: Contract or validated CRMLead with the same phone already exists.".format(  # noqa
                crm_lead.id
            ),
            crm_lead.action_set_remesa,
        )

    def test_crm_lead_action_set_remesa_location_change_existent_phone_number(self):
        crm_lead = crm_lead_create(self.env, self.partner_id, "mobile")

        # Same phone number from self.crm_lead
        crm_lead.lead_line_ids[0].mobile_isp_info.write(
            {"phone_number": self.crm_lead_mobile, "type": "location_change"}
        )
        crm_lead.action_set_remesa()

        self.assertTrue(crm_lead.skip_duplicated_phone_validation)

    def test_crm_lead_action_set_remesa_raise_error_with_duplicate_phone_number_in_new_line(  # noqa
        self,
    ):
        crm_lead = crm_lead_create(self.env, self.partner_id, "mobile")

        # Same phone number from self.crm_lead
        crm_lead.lead_line_ids[0].mobile_isp_info.write(
            {"phone_number": self.crm_lead_mobile}
        )

        self.assertEqual(crm_lead.stage_id, self.env.ref("crm.stage_lead1"))
        self.assertEqual(self.crm_lead.stage_id, self.env.ref("crm.stage_lead1"))
        self.assertRaisesRegex(
            ValidationError,
            "Error in {}: Duplicated phone number in CRMLead petitions.".format(
                crm_lead[0].id
            ),
            crm_lead.action_set_remesa,
        )

    def test_crm_lead_action_set_remesa_dont_raise_error_with_existent_phone_number_if_skip_true(  # noqa
        self,
    ):
        self.crm_lead.write(
            {
                "stage_id": self.env.ref("crm.stage_lead4").id,
            }
        )

        crm_lead = crm_lead_create(self.env, self.partner_id, "mobile")

        # Same phone number from self.crm_lead
        crm_lead.lead_line_ids[0].mobile_isp_info.write(
            {"phone_number": self.crm_lead_mobile}
        )
        crm_lead.skip_duplicated_phone_validation = True

        self.assertNotEqual(crm_lead.stage_id, self.env.ref("crm.stage_lead3"))
        crm_lead.action_set_remesa()
        self.assertEqual(crm_lead.stage_id, self.env.ref("crm.stage_lead3"))

    def test_crm_lead_action_set_remesa_dont_raise_error_with_existent_phone_number_if_dash(  # noqa
        self,
    ):
        adsl_crm_lead = crm_lead_create(self.env, self.partner_id, "adsl")
        adsl_crm_lead.broadband_lead_line_ids[0].broadband_isp_info.write(
            {"phone_number": "-"}
        )
        adsl_crm_lead.write(
            {
                "stage_id": self.env.ref("crm.stage_lead4").id,
            }
        )

        crm_lead = crm_lead_create(self.env, self.partner_id, "adsl")
        crm_lead.broadband_lead_line_ids[0].broadband_isp_info.write(
            {"phone_number": "-"}
        )

        self.assertNotEqual(crm_lead.stage_id, self.env.ref("crm.stage_lead3"))
        crm_lead.action_set_remesa()
        self.assertEqual(crm_lead.stage_id, self.env.ref("crm.stage_lead3"))

    def test_mobile_phone_number_portability_format_validation(self):
        crm_lead = crm_lead_create(
            self.env, self.partner_id, "mobile", portability=True
        )

        crm_lead.mobile_lead_line_ids[0].mobile_isp_info.write(
            {"phone_number": "497453838"}
        )

        self.assertRaisesRegex(
            ValidationError,
            "Mobile phone number has to be a 9 digit number starting with 6 or 7",
            crm_lead.action_set_remesa,
        )

    def test_broadband_phone_number_portability_format_validation(self):
        crm_lead = crm_lead_create(self.env, self.partner_id, "adsl", portability=True)
        crm_lead.broadband_lead_line_ids[0].broadband_isp_info.write(
            {"phone_number": "497453838"}
        )

        self.assertRaisesRegex(
            ValidationError,
            'Landline phone number has to be a dash "-" '
            "or a 9 digit number starting with 8 or 9",
            crm_lead.action_set_remesa,
        )

    def test_broadband_phone_number_portability_skip_format_validation(self):
        crm_lead = crm_lead_create(self.env, self.partner_id, "adsl", portability=True)
        crm_lead.broadband_lead_line_ids[0].broadband_isp_info.write(
            {"phone_number": "497453838"}
        )
        crm_lead.broadband_lead_line_ids[0].check_phone_number = True

        crm_lead.action_set_remesa()
        self.assertEqual(crm_lead.stage_id, self.env.ref("crm.stage_lead3"))

    def test_broadband_phone_number_portability_format_validation_dash(self):
        crm_lead = crm_lead_create(self.env, self.partner_id, "adsl", portability=True)
        crm_lead.broadband_lead_line_ids[0].broadband_isp_info.write(
            {"phone_number": "-"}
        )
        crm_lead._compute_phones_from_lead()

        crm_lead.action_set_remesa()
        self.assertEqual(crm_lead.stage_id, self.env.ref("crm.stage_lead3"))
        self.assertEqual(crm_lead.phones_from_lead, "[]")

    def test_crm_lead_right_pack(self):
        crm = crm_lead_create(self.env, self.partner_id, "pack")

        phones_from_lead = [
            crm.mobile_lead_line_ids[0].mobile_isp_info.phone_number,
            crm.broadband_lead_line_ids[0].broadband_isp_info.phone_number,
        ]

        self.assertTrue(crm)
        self.assertEqual(len(crm.mobile_lead_line_ids), 1)
        self.assertTrue(crm.has_broadband_lead_lines)
        self.assertEqual(len(crm.broadband_lead_line_ids), 1)
        self.assertTrue(crm.has_mobile_lead_lines)
        self.assertEqual(crm.phones_from_lead, str(phones_from_lead))

    def test_crm_lead_right_no_pack(self):
        self.assertTrue(
            self.env["crm.lead"].create(
                [
                    {
                        "name": "Test Lead",
                        "partner_id": self.partner_id.id,
                        "lead_line_ids": [
                            (0, 0, self.mobile_lead_line_vals),
                            (0, 0, self.mobile_lead_line_vals),
                        ],
                    }
                ]
            )
        )

    def test_crm_lead_right_pack_different_number(self):
        crm = crm_lead_create(self.env, self.partner_id, "pack")
        crm.write(
            {
                "lead_line_ids": [
                    (0, 0, self.mobile_lead_line_vals),
                ],
            }
        )

        self.assertTrue(crm)
        self.assertEqual(len(crm.broadband_lead_line_ids), 1)
        self.assertTrue(crm.has_broadband_lead_lines)
        self.assertEqual(len(crm.mobile_lead_line_ids), 2)
        self.assertTrue(crm.has_mobile_lead_lines)
        self.assertEqual(
            crm.phones_from_lead,
            str(
                [
                    crm.mobile_lead_line_ids[0].mobile_isp_info.phone_number,
                    crm.mobile_lead_line_ids[1].mobile_isp_info.phone_number,
                    crm.broadband_lead_line_ids[0].broadband_isp_info.phone_number,
                ]
            ),
        )

    def test_crm_lead_right_archive_crm_lead_line(self):
        crm_lead = crm_lead_create(self.env, self.partner_id, "pack", portability=True)
        mobile_crm_lead_line = crm_lead.lead_line_ids.filtered("is_mobile")

        self.assertTrue(mobile_crm_lead_line.active)

        mobile_crm_lead_line.toggle_active()

        self.assertFalse(mobile_crm_lead_line.active)

    def test_crm_lead_right_extra_product(self):
        crm_lead = crm_lead_create(
            self.env, self.partner_id, "mobile", portability=True
        )
        crm_lead.write(
            {
                "lead_line_ids": [
                    (0, 0, self.mobile_lead_line_vals),
                ],
            }
        )
        self.assertTrue(crm_lead)

    def test_crm_lead_right_single_pack_product(self):
        crm = crm_lead_create(self.env, self.partner_id, "mobile", portability=True)
        crm.mobile_lead_line_ids[0].mobile_isp_info.has_sim = True
        crm.mobile_lead_line_ids[0].product_id = (self.product_pack_mobile.id,)

        self.assertTrue(crm)
        self.assertFalse(crm.broadband_lead_line_ids)
        self.assertFalse(crm.has_broadband_lead_lines)
        self.assertEqual(len(crm.mobile_lead_line_ids), 1)
        self.assertTrue(crm.has_mobile_lead_lines)
        self.assertEqual(
            crm.phones_from_lead,
            str([crm.mobile_lead_line_ids[0].mobile_isp_info.phone_number]),
        )

    def test_crm_lead_action_set_won_right_pack(self):
        crm_lead = crm_lead_create(self.env, self.partner_id, "pack", portability=True)
        crm_lead.write(
            {
                "stage_id": self.env.ref("crm.stage_lead3").id,
            }
        )

        crm_lead.action_set_won()
        self.assertEqual(crm_lead.stage_id, self.env.ref("crm.stage_lead4"))

    def test_crm_lead_action_set_won_no_pack(self):
        crm_lead = crm_lead_create(
            self.env, self.partner_id, "mobile", portability=True
        )
        crm_lead.write(
            {
                "lead_line_ids": [
                    (0, 0, self.mobile_lead_line_vals),
                ],
                "stage_id": self.env.ref("crm.stage_lead3").id,
            }
        )
        crm_lead.action_set_won()
        self.assertEqual(crm_lead.stage_id, self.env.ref("crm.stage_lead4"))

    def test_crm_lead_action_set_won_right_pack_different_number(self):
        pack_crm_lead = crm_lead_create(
            self.env, self.partner_id, "pack", portability=True
        )
        self.mobile_lead_line_vals.update(
            {
                "product_id": self.product_pack_mobile.id,
            }
        )
        # add mobile lead line with pinya product
        pack_crm_lead.write(
            {
                "stage_id": self.env.ref("crm.stage_lead3").id,
                "lead_line_ids": [
                    (0, 0, self.mobile_lead_line_vals),
                ],
            }
        )

        pack_crm_lead.action_set_won()
        self.assertEqual(pack_crm_lead.stage_id, self.env.ref("crm.stage_lead4"))

    def test_crm_lead_action_set_won_right_pack_extra_product(self):
        crm_lead = crm_lead_create(self.env, self.partner_id, "pack", portability=True)
        crm_lead.write(
            {
                "lead_line_ids": [
                    (0, 0, self.mobile_lead_line_vals),
                ],
                "stage_id": self.env.ref("crm.stage_lead3").id,
            }
        )

        self.assertTrue(crm_lead)
        crm_lead.action_set_won()
        self.assertEqual(crm_lead.stage_id, self.env.ref("crm.stage_lead4"))

    def test_crm_lead_right_validation_single_pack_product(self):
        self.crm_lead.mobile_lead_line_ids[0].product_id = self.product_pack_mobile.id
        self.crm_lead.write(
            {
                "stage_id": self.env.ref("crm.stage_lead3").id,
            }
        )

        self.crm_lead.action_set_won()
        self.assertEqual(self.crm_lead.stage_id, self.env.ref("crm.stage_lead4"))

    def test_crm_lead_right_mobile_icc(self):
        self.env["ir.config_parameter"].set_param(
            "somconnexio.icc_start_sequence", "1234"
        )
        self.crm_lead.mobile_lead_line_ids[
            0
        ].mobile_isp_info.icc = "1234567890123456789"
        self.crm_lead.write({"stage_id": self.env.ref("crm.stage_lead3").id})

        self.crm_lead.action_set_won()

        self.assertEqual(self.crm_lead.stage_id, self.env.ref("crm.stage_lead4"))

    def test_crm_lead_wrong_mobile_icc_bad_prefix(self):
        self.env["ir.config_parameter"].set_param(
            "somconnexio.icc_start_sequence", "1234"
        )
        self.crm_lead.mobile_lead_line_ids[
            0
        ].mobile_isp_info.icc = "XXXX567890123456789"
        self.crm_lead.write({"stage_id": self.env.ref("crm.stage_lead3").id})

        self.assertRaisesRegex(
            ValidationError,
            "The value of ICC is not right: it must contain "
            "19 digits and starts with 1234",
            self.crm_lead.action_set_won,
        )

    def test_crm_lead_wrong_mobile_icc_bad_length(self):
        self.env["ir.config_parameter"].set_param(
            "somconnexio.icc_start_sequence", "1234"
        )
        self.crm_lead.mobile_lead_line_ids[0].mobile_isp_info.icc = "1234567890"
        self.crm_lead.write({"stage_id": self.env.ref("crm.stage_lead3").id})
        self.assertRaisesRegex(
            ValidationError,
            "The value of ICC is not right: it must contain "
            "19 digits and starts with 1234",
            self.crm_lead.action_set_won,
        )

    def test_crm_lead_wrong_mobile_icc_not_filled(self):
        self.env["ir.config_parameter"].set_param(
            "somconnexio.icc_start_sequence", "1234"
        )
        self.crm_lead.mobile_lead_line_ids[0].mobile_isp_info.icc = ""
        self.crm_lead.write({"stage_id": self.env.ref("crm.stage_lead3").id})
        self.assertRaisesRegex(
            ValidationError,
            "The ICC value of all mobile lines is not filled",
            self.crm_lead.action_set_won,
        )

    def test_crm_lead_broadband_w_fix_lead_line_ids(self):
        crm_lead = crm_lead_create(self.env, self.partner_id, "fiber", portability=True)
        ba_product_w_fix = self.env.ref("somconnexio.Fibra100Mb")
        crm_lead.broadband_lead_line_ids[0].product_id = ba_product_w_fix.id

        self.assertEqual(
            crm_lead.broadband_w_fix_lead_line_ids, crm_lead.broadband_lead_line_ids[0]
        )
        self.assertFalse(crm_lead.broadband_wo_fix_lead_line_ids)

    def test_crm_lead_broadband_wo_fix_lead_line_ids(self):
        crm_lead = crm_lead_create(self.env, self.partner_id, "fiber", portability=True)
        ba_product_wo_fix = self.env.ref("somconnexio.SenseFixFibra100Mb")
        crm_lead.broadband_lead_line_ids[0].product_id = ba_product_wo_fix.id

        self.assertEqual(
            crm_lead.broadband_wo_fix_lead_line_ids, crm_lead.broadband_lead_line_ids[0]
        )
        self.assertFalse(crm_lead.broadband_w_fix_lead_line_ids)

    def test_is_broadband_isp_info_type_location_change(self):
        broadband_isp_info_location_change = self.env["broadband.isp.info"].create(
            {"type": "location_change"}
        )
        crm_lead = crm_lead_create(self.env, self.partner_id, "fiber")
        crm_lead.lead_line_ids[
            0
        ].broadband_isp_info = broadband_isp_info_location_change.id

        crm_lead._compute_is_broadband_isp_info_type_location_change()

        self.assertTrue(crm_lead.is_broadband_isp_info_type_location_change)
