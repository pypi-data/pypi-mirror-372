from odoo import api, fields, models, _
from odoo.tools.misc import clean_context
from odoo.exceptions import ValidationError


class CustomPopMessage(models.TransientModel):
    _name = "custom.pop.message"
    name = fields.Char("Message")


class ContractCompensationWizard(models.TransientModel):
    _name = "contract.compensation.wizard"
    partner_id = fields.Many2one("res.partner")
    contract_ids = fields.Many2many("contract.contract")
    type = fields.Selection(
        [
            ("days_without_service", "Days without Service"),
            ("exact_amount", "Exact Amount"),
        ],
        "Compensation Type",
    )
    product_id = fields.Many2one(
        "product.product", "Product", related="contract_ids.tariff_product"
    )
    days_without_service = fields.Integer("Days without Service")
    exact_amount = fields.Float("Exact Amount")

    state = fields.Selection(
        [
            ("details", "details"),
            ("load", "load"),
        ],
        default="load",
    )

    days_without_service_import = fields.Float("Compensation amount")
    operation_date = fields.Date("Compensation date")
    description = fields.Char("Description")

    def button_compensate(self):
        if self.type == "days_without_service":
            if self.days_without_service <= 0.0:
                raise ValidationError(
                    _("The amount of days without service must be greater than zero")
                )
            tariff_product = self.product_id
            pricelist = self.env["product.pricelist"].search([("code", "=", "0IVA")])
            amount = (
                pricelist._compute_price_rule(tariff_product, 1)[tariff_product.id][0]
                / 30.0
                * self.days_without_service
            )
        else:
            amount = self.exact_amount
            if amount <= 0.0:
                raise ValidationError(_("The amount must be greater than zero €"))
        summary = _("The amount to compensate is %.2f €") % amount
        ctx = dict(
            clean_context(self.env.context),
            default_activity_type_id=self.env.ref(
                "somconnexio.mail_activity_type_sc_compensation"
            ).id,
            default_res_id=self.contract_ids.id,
            default_res_model_id=self.env.ref("contract.model_contract_contract").id,
            default_summary=summary,
            default_confirmation=True,
        )
        return {
            "name": _("Schedule an Activity"),
            "context": ctx,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.activity",
            "views": [(False, "form")],
            "type": "ir.actions.act_window",
            "target": "new",
        }

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults["partner_id"] = self.env.context["active_id"]
        return defaults

    @api.onchange("contract_ids")
    def onchange_contract_ids(self):
        if len(self.contract_ids) > 1:
            self.contract_ids = self.contract_ids[0]
            return {
                "warning": {
                    "title": _("Error"),
                    "message": _(
                        "You can only compensate one contract at the same time"
                    ),
                },
            }
