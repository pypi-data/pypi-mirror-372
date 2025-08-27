from ..sc_test_case import SCTestCase
from mock import Mock
from odoo.tests import patch


class TestMailComposerWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        mobile_isp_info = self.env["mobile.isp.info"].create(
            {
                "type": "new",
            }
        )
        crm_lead_line_args = {
            "name": "Test Crm Lead Line",
            "product_id": self.env["product.product"]
            .search(
                [("default_code", "=", "SE_SC_REC_MOBILE_T_0_2048")],
            )
            .id,
            "mobile_isp_info": mobile_isp_info.id,
            "broadband_isp_info": None,
        }
        self.crm_lead_line = self.env["crm.lead.line"].create([crm_lead_line_args])
        self.mock_with_context = Mock()
        self.mock_with_context.return_value.onchange_template_id.return_value = {
            "value": {}
        }  # noqa

    def test_mail_compose_template_catalan(self):
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")
        self.catalan_partner_crm_lead = self.env["crm.lead"].create(
            [
                {
                    "name": "Test catalan partner Lead",
                    "partner_id": self.partner_id.id,
                    "lead_line_ids": [(6, 0, [self.crm_lead_line.id])],
                }
            ]
        )
        wizard = self.env["mail.compose.message"].create(
            {
                "model": "crm.lead",
                "res_id": self.catalan_partner_crm_lead.id,
                "template_id": self.browse_ref(
                    "somconnexio.crm_lead_creation_email_template"
                ).id,
            }
        )
        with patch(
            "odoo.models.BaseModel.with_context", autospec=True
        ) as mock_with_context:
            wizard._onchange_template_id_wrapper()

            mock_with_context.assert_called_once_with(
                wizard,
                {
                    "lang": "ca_ES",
                    "tracking_disable": True,
                    "test_queue_job_no_delay": True,
                },
            )

    def test_mail_compose_template_spanish(self):
        partner_id = self.browse_ref("somconnexio.res_partner_2_demo")
        partner_id.lang = "es_ES"
        spanish_partner_crm_lead = self.env["crm.lead"].create(
            [
                {
                    "name": "Test catalan partner Lead",
                    "partner_id": partner_id.id,
                    "lead_line_ids": [(6, 0, [self.crm_lead_line.id])],
                }
            ]
        )
        wizard = self.env["mail.compose.message"].create(
            {
                "model": "crm.lead",
                "res_id": spanish_partner_crm_lead.id,
                "template_id": self.browse_ref(
                    "somconnexio.crm_lead_creation_email_template"
                ).id,
            }
        )
        with patch(
            "odoo.models.BaseModel.with_context", autospec=True
        ) as mock_with_context:
            wizard._onchange_template_id_wrapper()

            mock_with_context.assert_called_once_with(
                wizard,
                {
                    "lang": "es_ES",
                    "tracking_disable": True,
                    "test_queue_job_no_delay": True,
                },
            )
