from odoo import models, fields


class ServiceTechnology(models.Model):
    _name = "service.technology"
    name = fields.Char("Name")
    service_product_category_id = fields.Many2one(
        "product.category",
        help="Products category that provide service with recurring billing for a given technology.",  # noqa
    )
    external_provisioning_required = fields.Boolean(
        "Needs External Provisioning",
        help="If checked, the service needs to be provisioned by an external system.",  # noqa
        default=False,
    )
