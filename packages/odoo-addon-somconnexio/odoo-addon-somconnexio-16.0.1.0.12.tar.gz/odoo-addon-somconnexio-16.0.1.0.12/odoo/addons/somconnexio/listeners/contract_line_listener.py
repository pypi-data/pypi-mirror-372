from odoo import _
from odoo.addons.component.core import Component


class ContractLineListener(Component):
    _name = "contract.line.listener"
    _inherit = "base.event.listener"
    _apply_on = ["contract.line"]

    def on_record_create(self, record, fields=None):
        additional_service_products_categ_id_list = [
            self.env.ref("somconnexio.broadband_additional_service").id,
            self.env.ref("somconnexio.mobile_additional_service").id,
        ]

        if record.product_id.categ_id.id in additional_service_products_categ_id_list:
            message = _("Added product {} with start date {}").format(
                record.product_id.showed_name, record.date_start
            )
            record.contract_id.message_post(body=message)

    def on_record_write(self, record, fields=None):
        additional_service_products_categ_id_list = [
            self.env.ref("somconnexio.broadband_additional_service").id,
            self.env.ref("somconnexio.mobile_additional_service").id,
        ]
        if record.date_end:
            if (
                record.product_id.categ_id.id
                in additional_service_products_categ_id_list
            ):
                message = _("Updated product {} with end date {}").format(
                    record.product_id.showed_name, record.date_end
                )
                record.contract_id.message_post(body=message)
