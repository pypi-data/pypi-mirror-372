from ..sc_test_case import SCTestCase
from datetime import date
import base64


class TestContractInvoicePaymentWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        partner = self.browse_ref("somconnexio.res_partner_1_demo")
        partner_id = partner.id
        self.contract = self.env.ref("somconnexio.contract_fibra_600")
        self.contract_2 = self.env.ref("somconnexio.contract_adsl")
        date_invoice = date(2021, 1, 31)
        self.invoice = self.env["account.move"].create(
            {
                "partner_id": partner_id,
                "invoice_date": date_invoice,
                "name": "SO_invoice_test",
            }
        )
        self.invoice_2 = self.env["account.move"].create(
            {
                "partner_id": partner_id,
                "invoice_date": date_invoice,
                "name": "SO_invoice_test_2",
            }
        )

    def test_import_invoice_payment_ok(self):
        csv = (
            "Invoice number,Subscription code\n"
            f"{self.invoice.name},{self.contract.code}"
        )
        data = base64.b64encode(csv.encode("utf-8"))
        wizard = self.env["contract.invoice.payment.wizard"].create({"data": data})
        wizard.run_wizard()
        self.assertFalse(wizard.errors)
        self.assertEqual(self.invoice.mandate_id, self.contract.mandate_id)
        self.assertEqual(
            self.invoice.invoice_payment_term_id, self.contract.payment_term_id
        )
        self.assertEqual(self.invoice.payment_mode_id, self.contract.payment_mode_id)

    def test_import_invoice_payment_not_found_contract(self):
        csv = (
            "Invoice number,Subscription code\n"
            f"{self.invoice_2.name},{self.contract_2.code}\n"
            f"{self.invoice.name},XXX"
        )
        data = base64.b64encode(csv.encode("utf-8"))
        wizard = self.env["contract.invoice.payment.wizard"].create({"data": data})
        wizard.run_wizard()
        self.assertTrue(wizard.errors)
        self.assertEqual(self.invoice_2.mandate_id, self.contract_2.mandate_id)
        self.assertEqual(
            self.invoice_2.invoice_payment_term_id, self.contract_2.payment_term_id
        )
        self.assertEqual(
            self.invoice_2.payment_mode_id, self.contract_2.payment_mode_id
        )

    def test_import_invoice_payment_not_found_invoice(self):
        csv = (
            "Invoice number,Subscription code\n"
            f"XXX,{self.contract.code}\n"
            f"{self.invoice_2.name},{self.contract_2.code}"
        )
        data = base64.b64encode(csv.encode("utf-8"))
        wizard = self.env["contract.invoice.payment.wizard"].create({"data": data})
        wizard.run_wizard()
        self.assertTrue(wizard.errors)
        self.assertEqual(self.invoice_2.mandate_id, self.contract_2.mandate_id)
        self.assertEqual(
            self.invoice_2.invoice_payment_term_id, self.contract_2.payment_term_id
        )
        self.assertEqual(
            self.invoice_2.payment_mode_id, self.contract_2.payment_mode_id
        )

    def test_import_invoice_payment_ignore_dup_contract(self):
        self.contract_2.code = self.contract.code
        csv = (
            "Invoice number,Subscription code\n"
            f"{self.invoice.name},{self.contract.code}"
        )
        data = base64.b64encode(csv.encode("utf-8"))
        wizard = self.env["contract.invoice.payment.wizard"].create({"data": data})
        wizard.run_wizard()
        self.assertFalse(wizard.errors)
        self.assertEqual(self.invoice.mandate_id, self.contract.mandate_id)
        self.assertEqual(
            self.invoice.invoice_payment_term_id, self.contract.payment_term_id
        )
        self.assertEqual(self.invoice.payment_mode_id, self.contract.payment_mode_id)
