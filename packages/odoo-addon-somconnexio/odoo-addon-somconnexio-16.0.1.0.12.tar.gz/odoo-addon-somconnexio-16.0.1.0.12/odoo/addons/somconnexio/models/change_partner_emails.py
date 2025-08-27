from odoo import _, models


class ChangePartnerEmails(models.AbstractModel):
    _name = "change.partner.emails"
    _register = True
    _description = "Change Partner Emails"

    def _prepare_contract_change_write_data(self, emails):
        return {
            "email_ids": [(6, 0, [email.id for email in emails])],
        }

    def change_contact_email(self, partner, email):
        old_email = self._search_or_create_email(partner)
        partner.write({"email": email.email})
        message_partner = _("Email changed ({} --> {})")
        partner.message_post(message_partner.format(old_email.email, email.email))
        return True

    def change_contracts_emails(
        self,
        partner,
        contracts,
        emails,
        activity_args,
    ):
        for contract in contracts:
            # Post messages
            message_partner = _("Email changed ({} --> {}) in partner's contract '{}'")
            partner.message_post(
                message_partner.format(
                    ", ".join([email.email for email in contract.email_ids]),
                    ", ".join([email.email for email in emails]),
                    contract.name,
                )
            )
            message_contract = _("Contract email changed ({} --> {})")
            contract.message_post(
                message_contract.format(
                    ", ".join([email.email for email in contract.email_ids]),
                    ", ".join([email.email for email in emails]),
                )
            )
            # Update contracts
            contract.write(
                {
                    "email_ids": [(6, 0, [email.id for email in emails])],
                }
            )

            # Create activity
            self._create_activity(
                contract.id,
                activity_args,
            )

        return True

    def _create_activity(self, contract_id, activity_args):
        activity_args.update(
            {
                "res_id": contract_id,
            }
        )
        self.env["mail.activity"].with_context(mail_create_nosubscribe=True).create(
            activity_args
        )

    def _search_or_create_email(self, partner):
        """
        This method avoids duplicating emails.
        """
        email = self.env["res.partner"].search(
            [
                ("parent_id", "=", partner.id),
                ("email", "=", partner.email),
                ("type", "=", "contract-email"),
            ],
            limit=1,
        )
        if not email:
            email = self.env["res.partner"].create(
                {
                    "email": partner.email,
                    "parent_id": partner.id,
                    "type": "contract-email",
                }
            )
        return email
