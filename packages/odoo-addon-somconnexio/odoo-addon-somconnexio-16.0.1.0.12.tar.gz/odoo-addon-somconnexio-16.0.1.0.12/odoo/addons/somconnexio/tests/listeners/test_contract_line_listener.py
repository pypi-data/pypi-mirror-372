from mock import patch
from datetime import timedelta

from odoo import fields

from ..sc_test_case import SCComponentTestCase


class TestContractLineListener(SCComponentTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.ContractLine = self.env["contract.line"]
        self.international_mins = self.browse_ref("somconnexio.Internacional100Min")
        self.ip_fixa = self.browse_ref("somconnexio.IPv4Fixa")

        self.ba_contract = self.env.ref("somconnexio.contract_fibra_600")
        self.mobile_contract = self.env.ref("somconnexio.contract_mobile_il_20")

    @patch("odoo.addons.mail.models.mail_thread.MailThread.message_post")
    def test_create_line_with_mobile_additional_service(self, message_post_mock):
        self.ContractLine.create(
            {
                "name": self.international_mins.name,
                "contract_id": self.mobile_contract.id,
                "product_id": self.international_mins.id,
                "date_start": fields.Date.today(),
                "recurring_next_date": fields.Date.today() + timedelta(days=30),
            }
        )
        message_post_mock.assert_called_with(
            body="Added product {} with start date {}".format(
                self.international_mins.showed_name, fields.Date.today()
            )
        )

    @patch("odoo.addons.mail.models.mail_thread.MailThread.message_post")
    def test_create_line_with_ba_additional_service(self, message_post_mock):
        self.ContractLine.create(
            {
                "name": self.ip_fixa.name,
                "contract_id": self.ba_contract.id,
                "product_id": self.ip_fixa.id,
                "date_start": fields.Date.today(),
                "recurring_next_date": fields.Date.today() + timedelta(days=30),
            }
        )
        message_post_mock.assert_called_with(
            body="Added product {} with start date {}".format(
                self.ip_fixa.showed_name, fields.Date.today()
            )
        )

    @patch("odoo.addons.mail.models.mail_thread.MailThread.message_post")
    def test_terminate_line_enqueue_terminate_service(self, message_post_mock):
        cl = self.ContractLine.create(
            {
                "name": self.ip_fixa.name,
                "contract_id": self.ba_contract.id,
                "product_id": self.ip_fixa.id,
                "date_start": fields.Date.today(),
                "recurring_next_date": fields.Date.today() + timedelta(days=30),
            }
        )
        cl.write({"date_end": fields.Date.today()})
        message_post_mock.assert_called_with(
            body="Updated product {} with end date {}".format(
                self.ip_fixa.showed_name, fields.Date.today()
            )
        )
