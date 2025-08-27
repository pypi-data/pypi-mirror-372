from odoo.exceptions import ValidationError
from odoo.tests import common

from ...helpers.bank_utils import BankUtils


class TestBankUtils(common.TransactionCase):
    def setUp(self):
        super(TestBankUtils, self).setUp()
        self.env = self.env

    def test_extract_iban_from_list(self):
        bank_ids = [
            (0, 0, {"acc_number": "ES1234567890123456789012"}),
            (0, 0, {"acc_number": "ES2114650100722030876293"}),
            (0, 0, {"not_acc_number": "random"}),
        ]
        extracted_iban = BankUtils.extract_iban_from_list(bank_ids)
        self.assertEqual(extracted_iban, "ES2114650100722030876293")

    def test_validate_iban_valid(self):
        iban = "ES7921000813610123456789"
        try:
            BankUtils.validate_iban(iban, self.env)
        except ValidationError as e:
            self.fail(f"ValidationError raised wrongly: {e}")

    def test_validate_iban_invalid_format(self):
        iban = "ESES1234567890"
        self.assertRaisesRegex(
            ValidationError,
            "IBAN format is not correct. Example: ES21 1465 0100 72 2030876293",
            BankUtils.validate_iban,
            iban,
            self.env,
        )

    def test_validate_iban_invalid_bank(self):
        iban = "ES1234567890123456789012"
        self.assertRaisesRegex(
            ValidationError,
            "Error in ES1234567890123456789012: Invalid bank.",
            BankUtils.validate_iban,
            iban,
            self.env,
        )
