from datetime import date
from odoo import api, fields, models, _

boolean_selections = [
    ("yes", _("Yes")),
    ("no", "No"),
]


class PartnerEmailChangeWizard(models.TransientModel):
    _name = "partner.email.change.wizard"

    partner_id = fields.Many2one("res.partner")
    available_email_ids = fields.Many2many(
        "res.partner", string="Available Emails", compute="_compute_available_email_ids"
    )
    available_email_ids_for_partner = fields.Many2many(
        "res.partner",
        string="Available Emails for partner",
        compute="_compute_available_email_ids_for_partner",
    )

    # Change Contact Email fields
    change_contact_email = fields.Selection(
        string="Contact and OV", selection=boolean_selections, required=True
    )
    email_id = fields.Many2one(
        "res.partner",
        string="Email",
    )

    # Change Contracts Emails fields
    change_contracts_emails = fields.Selection(
        string="Contracts", selection=boolean_selections, required=True
    )
    contract_ids = fields.Many2many("contract.contract", string="Contracts")
    email_ids = fields.Many2many(
        "res.partner",
        string="Emails",
    )
    summary = fields.Char(translate=True, default="Email change")
    done = fields.Boolean(default=True)

    @api.depends("partner_id")
    def _compute_available_email_ids(self):
        if self.partner_id:
            self.available_email_ids = [
                (6, 0, self.partner_id.get_available_emails().ids)
            ]

    @api.depends("partner_id")
    def _compute_available_email_ids_for_partner(self):
        if self.partner_id:
            av_emails = self.partner_id.get_available_emails()
            email_ids = [e.id for e in av_emails if e.email != self.partner_id.email]
            self.available_email_ids_for_partner = [(6, 0, email_ids)]

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults["partner_id"] = self.env.context["active_id"]
        return defaults

    def button_change(self):
        self.ensure_one()
        change_partner_emails = self.env["change.partner.emails"]
        if self.change_contracts_emails == "yes":
            self._change_contract_emails(change_partner_emails)
        if self.change_contact_email == "yes":
            self._change_contact_email(change_partner_emails)

    def _change_contact_email(self, change_partner_emails):
        change_partner_emails.change_contact_email(self.partner_id, self.email_id)
        return True

    def _change_contract_emails(self, change_partner_emails):
        emails = self.email_ids or self.email_id
        activity_args = {
            "res_model_id": self.env.ref("contract.model_contract_contract").id,
            "user_id": self.env.user.id,
            "activity_type_id": self.env.ref(
                "somconnexio.mail_activity_type_contract_data_change"
            ).id,
            "date_done": date.today(),
            "date_deadline": date.today(),
            "summary": self.summary,
            "done": self.done,
        }
        change_partner_emails.change_contracts_emails(
            self.partner_id,
            self.contract_ids,
            emails,
            activity_args,
        )
        return True
