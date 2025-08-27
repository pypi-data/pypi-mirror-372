from ..sc_test_case import SCTestCase
from unittest.mock import patch


class TestServerAction(SCTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestServerAction, cls).setUpClass()
        # disable tracking test suite wise
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                test_queue_job_no_delay=False,
            )
        )

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.QueueJob = self.env["queue.job"]
        self.partner = self.browse_ref("somconnexio.res_partner_2_demo")
        product_id = self.browse_ref("somconnexio.Fibra100Mb")
        broadband_isp_info = self.env["broadband.isp.info"].create(
            {
                "type": "new",
                "phone_number": "98282082",
            }
        )
        self.line_params = {
            "name": product_id.name,
            "product_id": product_id.id,
            "product_tmpl_id": product_id.product_tmpl_id.id,
            "category_id": product_id.product_tmpl_id.categ_id.id,
            "broadband_isp_info": broadband_isp_info.id,
        }
        self.jobs_domain = [
            ("method_name", "=", "_send_background_email"),
            ("model_name", "=", "ir.actions.server"),
        ]
        self.queued_jobs_before = self.QueueJob.search(self.jobs_domain)

        self.server_action = self.env["ir.actions.server"].search(
            [
                ("name", "=", "Send email on CRM Lead creation"),
                ("state", "=", "background_email"),
            ]
        )

    def test_run_action_background_email(self):
        self.assertFalse(self.queued_jobs_before)

        lead_line = self.env["crm.lead.line"].create(self.line_params)
        crm_lead = self.env["crm.lead"].create(
            [
                {
                    "name": "Test Lead",
                    "partner_id": self.partner.id,
                    "lead_line_ids": [(6, 0, [lead_line.id])],
                }
            ]
        )

        # The trigger from the base automation 'send_email_on_crm_lead_creation'
        # does not work automatically with odoo testing, so in here we will be forcing
        # the method execution ('run_action_background_email')
        self.server_action.with_context(
            active_id=crm_lead.id
        ).run_action_background_email("")

        queued_jobs_after = self.QueueJob.search(self.jobs_domain)
        self.assertEqual(1, len(queued_jobs_after))

    def test_do_not_run_action_background_email_change_address(self):
        self.assertFalse(self.queued_jobs_before)

        lc_broadband_isp_info = self.env["broadband.isp.info"].create(
            {
                "type": "location_change",
                "phone_number": "98282082",
            }
        )
        self.line_params.update({"broadband_isp_info": lc_broadband_isp_info.id})
        lead_line = self.env["crm.lead.line"].create(self.line_params)
        crm_lead = self.env["crm.lead"].create(
            [
                {
                    "name": "Test Lead",
                    "partner_id": self.partner.id,
                    "lead_line_ids": [(6, 0, [lead_line.id])],
                }
            ]
        )
        self.server_action.with_context(
            active_id=crm_lead.id
        ).run_action_background_email("")

        queued_jobs_after = self.QueueJob.search(self.jobs_domain)
        self.assertFalse(queued_jobs_after)

    def test_do_not_run_action_background_email_ba_change_holder(self):
        self.assertFalse(self.queued_jobs_before)

        hc_broadband_isp_info = self.env["broadband.isp.info"].create(
            {
                "type": "holder_change",
                "phone_number": "98282082",
            }
        )
        self.line_params.update({"broadband_isp_info": hc_broadband_isp_info.id})
        lead_line = self.env["crm.lead.line"].create(self.line_params)
        crm_lead = self.env["crm.lead"].create(
            [
                {
                    "name": "Test Lead",
                    "partner_id": self.partner.id,
                    "lead_line_ids": [(6, 0, [lead_line.id])],
                }
            ]
        )
        self.server_action.with_context(
            active_id=crm_lead.id
        ).run_action_background_email("")

        queued_jobs_after = self.QueueJob.search(self.jobs_domain)
        self.assertFalse(queued_jobs_after)

    def test_do_not_run_action_background_email_mbl_change_holder(self):
        self.assertFalse(self.queued_jobs_before)

        hc_mobile_isp_info = self.env["mobile.isp.info"].create(
            {
                "type": "holder_change",
                "phone_number": "98282082",
            }
        )
        self.line_params.update({"mobile_isp_info": hc_mobile_isp_info.id})
        lead_line = self.env["crm.lead.line"].create(self.line_params)
        crm_lead = self.env["crm.lead"].create(
            [
                {
                    "name": "Test Lead",
                    "partner_id": self.partner.id,
                    "lead_line_ids": [(6, 0, [lead_line.id])],
                }
            ]
        )
        self.server_action.with_context(
            active_id=crm_lead.id
        ).run_action_background_email("")

        queued_jobs_after = self.QueueJob.search(self.jobs_domain)
        self.assertFalse(queued_jobs_after)

    @patch(
        "odoo.addons.mail.models.ir_actions_server.ServerActions._run_action_mail_post_multi"  # noqa: E501
    )
    def test_run_action_background_email_with_delay(self, mock_send_email):
        self.server_action._send_background_email(self.server_action, _active_id=1)
        mock_send_email.assert_called_once()
