# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models

_log = logging.getLogger(__name__)


class ServerActions(models.Model):
    """Add email option in server actions."""

    _name = "ir.actions.server"
    _description = "Server Action"
    _inherit = ["ir.actions.server"]

    state = fields.Selection(
        selection_add=[
            ("background_email", "Send Email in Background"),
        ],
        ondelete={"background_email": "set default"},
    )

    def run_action_background_email(self, action, eval_context=None):
        active_id = self.env.context["active_id"]
        # Do not send mails for change address/holder crm lead lines
        crm_lead = self.env["crm.lead"].browse(active_id)
        crm_lead_line = crm_lead.lead_line_ids[0]
        if (
            crm_lead_line.broadband_isp_info
            and crm_lead_line.broadband_isp_info.type
            in ["location_change", "holder_change"]
            or (
                crm_lead_line.mobile_isp_info
                and crm_lead_line.mobile_isp_info.type == "holder_change"
            )
        ):
            return

        self.with_delay()._send_background_email(action, _active_id=active_id)
        crm_lead.email_sent = True

    def _send_background_email(self, action, _active_id):
        # TODO -> Review the role of action in this method
        self = self.with_context({"active_id": _active_id})
        eval_context = self._get_eval_context(action)
        _log.info("Sending email in background with context:\n{}".format(self._context))
        self._run_action_mail_post_multi(eval_context)
