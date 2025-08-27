import re
from odoo import _
from odoo.exceptions import ValidationError
from odoo.addons.base_iban.models.res_partner_bank import (
    normalize_iban,
    pretty_iban,
    _map_iban_template,
)


class BankUtils:
    @staticmethod
    def extract_iban_from_list(bank_ids):
        extracted_iban = ""

        for bank_info in bank_ids:
            if isinstance(bank_info, (list, tuple)) and isinstance(bank_info[2], dict):
                acc_number = bank_info[2].get("acc_number", "")
                if acc_number:
                    extracted_iban = acc_number
        return extracted_iban

    @staticmethod
    def _get_bank(iban, env):
        # Code copied from base_bank_from_iban module:
        # https://github.com/OCA/community-data-files/blob/12.0/base_bank_from_iban/models/res_partner_bank.py#L13  # noqa
        acc_number = pretty_iban(normalize_iban(iban)).upper()
        country_code = acc_number[:2].lower()
        iban_template = _map_iban_template[country_code]
        first_match = iban_template[2:].find("B") + 2
        last_match = iban_template.rfind("B") + 1
        bank_code = acc_number[first_match:last_match].replace(" ", "")
        bank = (
            env["res.bank"]
            .sudo()
            .search(
                [
                    ("code", "=", bank_code),
                    ("country.code", "=", country_code.upper()),
                ],
                limit=1,
            )
        )
        return bank

    @staticmethod
    def validate_iban(iban, env):
        acc_number = iban.replace(" ", "").upper()
        if not re.match(r"^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$", acc_number):
            raise ValidationError(
                _("IBAN format is not correct. Example: ES21 1465 0100 72 2030876293")
            )

        bank = BankUtils._get_bank(iban, env)
        if not bank:
            raise ValidationError(_("Error in {}: Invalid bank.").format(iban))
