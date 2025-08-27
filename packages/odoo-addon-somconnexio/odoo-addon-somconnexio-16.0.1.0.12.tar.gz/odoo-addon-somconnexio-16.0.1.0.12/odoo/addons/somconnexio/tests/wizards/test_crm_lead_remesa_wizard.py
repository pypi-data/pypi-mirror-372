from odoo.exceptions import ValidationError
from ..sc_test_case import SCTestCase
from ..helper_service import crm_lead_create


class TestCRMLeadsRemesaWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")
        self.crm_lead = crm_lead_create(
            self.env, self.partner_id, "mobile", portability=True
        )

    def test_wizard_OK(self):
        wizard = (
            self.env["crm.lead.remesa.wizard"]
            .with_context(active_ids=[self.crm_lead.id])
            .create({})
        )
        wizard.button_remesa()
        self.assertEqual(self.crm_lead.stage_id, self.browse_ref("crm.stage_lead3"))
        self.assertFalse(wizard.errors)

    def test_wizard_KO(self):
        existing_crm_lead = crm_lead_create(
            self.env, self.partner_id, "mobile", portability=True
        )
        existing_crm_lead.lead_line_ids[0].mobile_isp_info.write(
            {
                "phone_number": self.crm_lead.lead_line_ids[
                    0
                ].mobile_isp_info_phone_number  # noqa
            }
        )
        # save as validated/won
        existing_crm_lead.write({"stage_id": self.browse_ref("crm.stage_lead4").id})

        wizard = (
            self.env["crm.lead.remesa.wizard"]
            .with_context(active_ids=[self.crm_lead.id])
            .create({})
        )

        self.assertEqual(
            wizard.errors,
            "The next CRMLeadLines have a phone number that already exists in another contract/CRMLead: {}".format(  # noqa
                self.crm_lead.id
            ),
        )
        self.assertRaises(ValidationError, wizard.button_remesa)
