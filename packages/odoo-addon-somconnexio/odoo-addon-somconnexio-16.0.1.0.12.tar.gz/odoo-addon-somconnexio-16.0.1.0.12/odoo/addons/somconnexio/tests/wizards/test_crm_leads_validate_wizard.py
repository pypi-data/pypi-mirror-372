from ..sc_test_case import SCTestCase
from ..helper_service import random_icc


class TestCRMLeadsValidateWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.crm_lead = self.env["crm.lead"].create([{"name": "Test Lead"}])
        self.crm_lead_line_args = {
            "name": "666666666",
            "product_id": "666666666",
            "mobile_isp_info": None,
            "broadband_isp_info": None,
        }
        self.mobile_isp_info = self.env["mobile.isp.info"].create(
            {
                "type": "new",
                "icc": random_icc(self.env),
            }
        )
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")

        mobile_product_tmpl_args = {
            "name": "Sense minutes",
            "type": "service",
            "categ_id": self.ref("somconnexio.mobile_service"),
        }
        product_mobile_tmpl = self.env["product.template"].create(
            mobile_product_tmpl_args
        )
        self.product_mobile = product_mobile_tmpl.product_variant_id

    def test_wizard_ok(self):
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
        self.crm_lead.write(
            {
                "lead_line_ids": [(6, 0, [mobile_crm_lead_line.id])],
                "stage_id": self.browse_ref("crm.stage_lead3").id,
            }
        )
        wizard = (
            self.env["crm.lead.validate.wizard"]
            .with_context(active_ids=[self.crm_lead.id])
            .create({"crm_lead_ids": [(6, 0, [self.crm_lead.id])]})
        )
        wizard.button_validate()
        self.assertEqual(self.crm_lead.stage_id, self.browse_ref("crm.stage_lead4"))

    def test_ensure_crm_lead_line_iban_in_partner_validate_wizard(self):
        crm_lead_line_iban = "ES6621000418401234567891"
        crm_lead_line_args_copy = self.crm_lead_line_args.copy()
        crm_lead_line_args_copy.update(
            {
                "mobile_isp_info": self.mobile_isp_info.id,
                "product_id": self.product_mobile.id,
                "iban": crm_lead_line_iban,
            }
        )
        mobile_crm_lead_line = self.env["crm.lead.line"].create(
            [crm_lead_line_args_copy]
        )
        crm_lead = self.env["crm.lead"].create(
            [
                {
                    "name": "Test Lead",
                    "partner_id": self.partner_id.id,
                    "lead_line_ids": [(6, 0, [mobile_crm_lead_line.id])],
                    "stage_id": self.browse_ref("crm.stage_lead3").id,
                }
            ]
        )
        self.assertEqual(len(self.partner_id.bank_ids), 1)
        self.assertNotIn(
            crm_lead_line_iban, self.partner_id.bank_ids.mapped("sanitized_acc_number")
        )

        wizard = (
            self.env["crm.lead.validate.wizard"]
            .with_context(active_ids=[crm_lead.id])
            .create({"crm_lead_ids": [(6, 0, [crm_lead.id])]})
        )
        wizard.button_validate()

        self.assertEqual(len(self.partner_id.bank_ids), 2)
        self.assertIn(
            crm_lead_line_iban, self.partner_id.bank_ids.mapped("sanitized_acc_number")
        )
