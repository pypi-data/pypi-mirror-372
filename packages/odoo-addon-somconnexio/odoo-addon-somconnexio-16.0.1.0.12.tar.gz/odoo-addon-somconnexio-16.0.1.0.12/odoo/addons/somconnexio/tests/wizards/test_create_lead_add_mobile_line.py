from ..helper_service import crm_lead_create
from ..sc_test_case import SCTestCase


class TestCRMLeadAddMobileLine(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")

    def test_create_line(self):
        fiber_crm_lead = crm_lead_create(
            self.env, self.partner_id, "fiber", portability=False
        )

        self.assertFalse(fiber_crm_lead.has_mobile_lead_lines)

        wizard_vals = {
            "product_id": self.env.ref("somconnexio.TrucadesIllimitades20GB").id,
            "icc": "1234ICC",
            "type": "new",
            "bank_id": self.partner_id.bank_ids.id,
        }
        wizard = (
            self.env["crm.lead.add.mobile.line.wizard"]
            .with_context(active_id=fiber_crm_lead.id)
            .create(wizard_vals)
        )

        wizard.button_create()

        self.assertTrue(fiber_crm_lead.has_mobile_lead_lines)

        self.assertEqual(len(fiber_crm_lead.mobile_lead_line_ids), 1)

        crm_lead_line = fiber_crm_lead.mobile_lead_line_ids[0]

        self.assertEqual(
            crm_lead_line.product_id.id,
            wizard_vals["product_id"],
        )
        self.assertEqual(
            crm_lead_line.iban,
            self.partner_id.bank_ids.sanitized_acc_number,
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.icc,
            wizard_vals["icc"],
        )
        self.assertEqual(
            crm_lead_line.mobile_isp_info.type,
            wizard_vals["type"],
        )
