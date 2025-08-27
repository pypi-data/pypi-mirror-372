from odoo import api, fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    is_mobile_tariff_service = fields.Boolean(
        compute="_compute_is_mobile_tariff",
    )

    @api.depends("product_id")
    def _compute_is_mobile_tariff(self):
        mobile_tariff_service = self.env.ref("somconnexio.mobile_service")
        for record in self:
            record.is_mobile_tariff_service = (
                record.product_id.categ_id == mobile_tariff_service
            )
