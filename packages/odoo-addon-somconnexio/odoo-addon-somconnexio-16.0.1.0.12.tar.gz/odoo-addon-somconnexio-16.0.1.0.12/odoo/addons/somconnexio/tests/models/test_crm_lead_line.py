from ..sc_test_case import SCTestCase
from odoo.exceptions import ValidationError


class CRMLeadLineTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")
        self.partner_iban = self.partner_id.bank_ids[0].sanitized_acc_number

        self.crm_lead_line_args = {
            "name": "666666666",
            "product_id": "666666666",
            "mobile_isp_info": None,
            "broadband_isp_info": None,
            "iban": self.partner_iban,
        }

        self.mobile_isp_info = self.env["mobile.isp.info"].create(
            {
                "type": "new",
            }
        )
        self.broadband_isp_info = self.env["broadband.isp.info"].create(
            {
                "phone_number": "666666666",
                "type": "new",
            }
        )

        self.product_broadband_adsl = self.browse_ref("somconnexio.ADSL20MBSenseFix")
        self.product_broadband_fiber = self.browse_ref("somconnexio.Fibra100Mb")
        self.product_mobile = self.browse_ref("somconnexio.SenseMinutsSenseDades")
        self.product_pack_mobile = self.browse_ref(
            "somconnexio.TrucadesIllimitades20GBPack"
        )

    def test_mobile_lead_line_creation_ok(self):
        crm_lead_line_args_copy = self.crm_lead_line_args.copy()
        crm_lead_line_args_copy.update(
            {
                "mobile_isp_info": self.mobile_isp_info.id,
                "product_id": self.product_mobile.id,
            }
        )

        mobile_crm_lead_line = self.env["crm.lead.line"].create(
            [crm_lead_line_args_copy]
        )
        self.assertTrue(mobile_crm_lead_line.id)
        self.assertTrue(mobile_crm_lead_line.is_mobile)
        self.assertFalse(mobile_crm_lead_line.is_from_pack)
        self.assertEqual(mobile_crm_lead_line.iban, self.partner_iban)

    def test_broadband_lead_line_creation_ok(self):
        crm_lead_line_args_copy = self.crm_lead_line_args.copy()
        crm_lead_line_args_copy.update(
            {
                "broadband_isp_info": self.broadband_isp_info.id,
                "product_id": self.product_broadband_adsl.id,
            }
        )

        broadband_crm_lead_line = self.env["crm.lead.line"].create(
            [crm_lead_line_args_copy]
        )
        self.assertTrue(broadband_crm_lead_line.id)
        self.assertTrue(broadband_crm_lead_line.is_adsl)
        self.assertEqual(broadband_crm_lead_line.iban, self.partner_iban)

    def test_broadband_4G_lead_line_creation_ok(self):
        self.broadband_isp_info.update({"phone_number": "-"})
        crm_lead_line_args_copy = self.crm_lead_line_args.copy()
        crm_lead_line_args_copy.update(
            {
                "broadband_isp_info": self.broadband_isp_info.id,
                "product_id": self.env.ref("somconnexio.Router4G").id,
            }
        )

        broadband_crm_lead_line = self.env["crm.lead.line"].create(
            [crm_lead_line_args_copy]
        )
        self.assertTrue(broadband_crm_lead_line.id)
        self.assertTrue(broadband_crm_lead_line.is_4G)

    def test_broadband_lead_line_creation_without_broadband_isp_info(self):
        crm_lead_line_args_copy = self.crm_lead_line_args.copy()
        crm_lead_line_args_copy.update({"product_id": self.product_broadband_adsl.id})

        self.assertRaises(
            ValidationError, self.env["crm.lead.line"].create, [crm_lead_line_args_copy]
        )

    def test_mobile_lead_line_creation_without_mobile_isp_info(self):
        crm_lead_line_args_copy = self.crm_lead_line_args.copy()
        crm_lead_line_args_copy.update({"product_id": self.product_mobile.id})

        self.assertRaises(
            ValidationError, self.env["crm.lead.line"].create, [crm_lead_line_args_copy]
        )

    def test_broadband_check_phone_number_on_change(self):
        crm_lead_line_args_copy = self.crm_lead_line_args.copy()
        crm_lead_line_args_copy.update(
            {
                "broadband_isp_info": self.broadband_isp_info.id,
                "product_id": self.product_broadband_adsl.id,
            }
        )
        ba_crm_lead_line = self.env["crm.lead.line"].create([crm_lead_line_args_copy])
        self.env["crm.lead"].create(
            [
                {
                    "name": "Test Lead",
                    "lead_line_ids": [(6, 0, [ba_crm_lead_line.id])],
                    "stage_id": self.env.ref("crm.stage_lead1").id,
                }
            ]
        )
        self.assertFalse(ba_crm_lead_line.lead_id.skip_duplicated_phone_validation)
        ba_crm_lead_line.check_phone_number = True
        ba_crm_lead_line._onchange_check_phone_number()
        self.assertTrue(ba_crm_lead_line.lead_id.skip_duplicated_phone_validation)

    def test_update_mobile_isp_info_has_sim(self):
        crm_lead = self.env["crm.lead"].create(
            [{"name": "Test Lead", "partner_id": self.partner_id.id}]
        )
        crm_lead_line_args_copy = self.crm_lead_line_args.copy()
        crm_lead_line_args_copy.update(
            {
                "lead_id": crm_lead.id,
                "mobile_isp_info": self.mobile_isp_info.id,
                "product_id": self.product_mobile.id,
            }
        )
        mobile_crm_lead_line = self.env["crm.lead.line"].create(
            [crm_lead_line_args_copy]
        )
        self.assertFalse(self.mobile_isp_info.has_sim)
        mobile_crm_lead_line.mobile_isp_info_has_sim = True
        self.assertTrue(self.mobile_isp_info.has_sim)

    def test_mobile_pack_lead_line_creation_ok(self):
        crm_lead_line_args_copy = self.crm_lead_line_args.copy()
        crm_lead_line_args_copy.update(
            {
                "mobile_isp_info": self.mobile_isp_info.id,
                "product_id": self.product_pack_mobile.id,
            }
        )

        mobile_crm_lead_line = self.env["crm.lead.line"].create(
            [crm_lead_line_args_copy]
        )
        self.assertTrue(mobile_crm_lead_line.id)
        self.assertTrue(mobile_crm_lead_line.is_mobile)
        self.assertTrue(mobile_crm_lead_line.is_from_pack)
