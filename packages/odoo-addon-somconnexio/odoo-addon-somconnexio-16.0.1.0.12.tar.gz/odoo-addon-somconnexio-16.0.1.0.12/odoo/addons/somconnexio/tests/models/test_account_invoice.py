from ..sc_test_case import SCTestCase
from odoo.exceptions import UserError


class AccountInvoice(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.res_partner_bank_0 = (
            self.env["res.partner.bank"]
            .with_user(self.account_manager.id)
            .create(
                dict(
                    acc_type="bank",
                    company_id=self.main_company.id,
                    partner_id=self.main_partner.id,
                    acc_number="123456789",
                    bank_id=self.main_bank.id,
                )
            )
        )
        self.account_invoice_obj = self.env["account.move"]
        self.payment_term = self.env.ref("account.account_payment_term_advance")
        self.journalrec = self.env["account.journal"].search([("type", "=", "sale")])[0]
        self.partner3 = self.env.ref("base.res_partner_3")
        account_user_type = self.env.ref("account.data_account_type_receivable")
        self.ova = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_current_assets").id,
                )
            ],
            limit=1,
        )
        self.account_rec1_id = self.account_model.with_user(
            self.account_manager.id
        ).create(
            dict(
                code="cust_acc",
                name="customer account",
                user_type_id=account_user_type.id,
                reconcile=True,
            )
        )

        invoice_line_data = [
            (
                0,
                0,
                {
                    "product_id": self.env.ref("product.product_product_5").id,
                    "quantity": 10.0,
                    "account_id": self.env["account.account"]
                    .search(
                        [
                            (
                                "user_type_id",
                                "=",
                                self.env.ref("account.data_account_type_revenue").id,
                            )
                        ],
                        limit=1,
                    )
                    .id,
                    "name": "product test 5",
                    "price_unit": 100.00,
                },
            )
        ]

        self.account_invoice_customer0 = self.account_invoice_obj.with_user(
            self.account_user.id
        ).create(
            dict(
                name="Test Customer Invoice",
                payment_term_id=self.payment_term.id,
                journal_id=self.journalrec.id,
                partner_id=self.partner3.id,
                account_id=self.account_rec1_id.id,
                invoice_line_ids=invoice_line_data,
            )
        )

    def test_customer_invoice(self):
        # I check that Initially customer invoice is in the "Draft" state
        self.assertEqual(self.account_invoice_customer0.state, "draft")

        # I check that there is no move attached to the invoice
        self.assertEqual(len(self.account_invoice_customer0.move_id), 0)

        # I validate invoice by creating on
        self.account_invoice_customer0.action_invoice_open()

        # I check that the invoice state is "Open"
        self.assertEqual(self.account_invoice_customer0.state, "open")

    def test_customer_invoice_archived_journal(self):
        # I check that Initially customer invoice is in the "Draft" state
        self.assertEqual(self.account_invoice_customer0.state, "draft")

        # I check that there is no move attached to the invoice
        self.assertEqual(len(self.account_invoice_customer0.move_id), 0)

        self.account_invoice_customer0.journal_id.active = False
        # I validate invoice by creating on
        self.assertRaises(UserError, self.account_invoice_customer0.action_invoice_open)
