import unittest
from odoo.tests.common import TransactionCase


class TestPaymentOrderInbound(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.inbound_mode = self.env.ref(
            "account_payment_mode.payment_mode_inbound_dd1"
        )
        self.journal = self.env["account.journal"].search(
            [
                ("type", "=", "bank"),
                "|",
                ("company_id", "=", self.env.user.company_id.id),
                ("company_id", "=", False),
            ],
            limit=1,
        )
        if not self.journal:
            raise unittest.SkipTest("No journal found")
        self.inbound_mode.variable_journal_ids = self.journal
        # Make sure no others orders are present
        self.domain = [
            ("state", "=", "draft"),
            ("payment_type", "=", "inbound"),
        ]
        self.payment_order_obj = self.env["account.payment.order"]
        self.payment_order_obj.search(self.domain).unlink()
        # Create payment order
        self.inbound_order = self.env["account.payment.order"].create(
            {
                "payment_type": "inbound",
                "payment_mode_id": self.inbound_mode.id,
                "journal_id": self.journal.id,
            }
        )
        self.invoice_line_account = (
            self.env["account.account"]
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
            .id
        )
        self.invoice_account = (
            self.env["account.account"]
            .search(
                [
                    (
                        "user_type_id",
                        "=",
                        self.env.ref("account.data_account_type_receivable").id,
                    )
                ],
                limit=1,
            )
            .id
        )

    def test_creation_phone(self):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.env.ref("base.res_partner_4").id,
                "type": "out_invoice",
                "payment_mode_id": self.inbound_mode.id,
                "account_id": self.invoice_account,
                "journal_id": self.ref("somconnexio.consumption_invoices_journal"),
                "name": "SO2021-1234",
            }
        )
        self.env["account.move.line"].create(
            {
                "product_id": self.env.ref("product.product_product_4").id,
                "quantity": 1.0,
                "price_unit": 100.0,
                "invoice_id": invoice.id,
                "name": "product that cost 100",
                "account_id": self.invoice_line_account,
            }
        )
        invoice.action_invoice_open()
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=invoice.ids
        ).create({}).run()
        payment_order = self.inbound_order
        payment_order.draft2open()
        self.assertEqual(len(payment_order.payment_line_ids), 1)
        self.assertEqual(payment_order.payment_line_ids.purpose, "PHON")

    def test_creation_not_phone(self):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.env.ref("base.res_partner_4").id,
                "type": "out_invoice",
                "payment_mode_id": self.inbound_mode.id,
                "account_id": self.invoice_account,
            }
        )
        self.env["account.move.line"].create(
            {
                "product_id": self.env.ref("product.product_product_4").id,
                "quantity": 1.0,
                "price_unit": 100.0,
                "invoice_id": invoice.id,
                "name": "product that cost 100",
                "account_id": self.invoice_line_account,
            }
        )
        invoice.action_invoice_open()
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=invoice.ids
        ).create({}).run()
        payment_order = self.inbound_order
        payment_order.draft2open()
        self.assertEqual(len(payment_order.payment_line_ids), 1)
        self.assertFalse(payment_order.payment_line_ids.purpose)
