from mock import patch
from datetime import date


from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.addons.somconnexio.tests.helper_service import contract_fiber_create_data


class TestPartnerEmailChangeWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner = self.env.ref("somconnexio.res_partner_2_demo")
        vals_contract = contract_fiber_create_data(self.env, self.partner)
        self.Contract = self.env["contract.contract"]
        self.contract = self.Contract.create(vals_contract)
        vals_contract_same_partner = vals_contract.copy()
        vals_contract_same_partner.update({"name": "Test Contract Broadband B"})
        self.contract_same_partner = self.Contract.create(vals_contract_same_partner)
        self.partner_email_b = self.env["res.partner"].create(
            {
                "name": "Email b",
                "email": "email_b@example.org",
                "type": "contract-email",
                "parent_id": self.env.ref("somconnexio.res_partner_2_demo").id,
            }
        )
        self.user_admin = self.browse_ref("base.user_admin")
        self.expected_activity_args = {
            "res_model_id": self.env.ref("contract.model_contract_contract").id,
            "user_id": self.user_admin.id,
            "activity_type_id": self.env.ref(
                "somconnexio.mail_activity_type_contract_data_change"
            ).id,  # noqa
            "date_done": date.today(),
            "date_deadline": date.today(),
            "summary": "Email change",
            "done": True,
        }

    @patch(
        "odoo.addons.somconnexio.models.change_partner_emails.ChangePartnerEmails.change_contracts_emails",  # noqa
    )
    def test_change_contracts_emails_one_email_change_ok(
        self, mock_change_contracts_emails
    ):  # noqa
        wizard = (
            self.env["partner.email.change.wizard"]
            .with_context(active_id=self.partner.id)
            .with_user(self.user_admin)
            .create(
                {
                    "change_contact_email": "no",
                    "change_contracts_emails": "yes",
                    "contract_ids": [
                        (6, 0, [self.contract_same_partner.id, self.contract.id])
                    ],
                    "email_ids": [(6, 0, [self.partner_email_b.id])],
                }
            )
        )
        self.assertFalse("start_date" in dir(wizard))
        wizard.button_change()
        mock_change_contracts_emails.assert_called_once_with(  # noqa
            self.partner,
            self.Contract.browse([self.contract_same_partner.id, self.contract.id]),
            self.partner_email_b,
            self.expected_activity_args,
        )

    @patch(
        "odoo.addons.somconnexio.models.change_partner_emails.ChangePartnerEmails.change_contracts_emails",  # noqa
    )
    def test_change_contracts_emails_many_email_change_ok(
        self, mock_change_contracts_emails
    ):
        self.env["partner.email.change.wizard"].with_context(
            active_id=self.partner.id
        ).with_user(self.user_admin).create(
            {
                "change_contact_email": "no",
                "change_contracts_emails": "yes",
                "contract_ids": [
                    (6, 0, [self.contract_same_partner.id, self.contract.id])
                ],
                "email_ids": [(6, 0, [self.partner_email_b.id, self.partner.id])],
            }
        ).button_change()

        mock_change_contracts_emails.assert_called_once_with(
            self.partner,
            self.Contract.browse([self.contract_same_partner.id, self.contract.id]),
            self.env["res.partner"].browse([self.partner_email_b.id, self.partner.id]),
            self.expected_activity_args,
        )
