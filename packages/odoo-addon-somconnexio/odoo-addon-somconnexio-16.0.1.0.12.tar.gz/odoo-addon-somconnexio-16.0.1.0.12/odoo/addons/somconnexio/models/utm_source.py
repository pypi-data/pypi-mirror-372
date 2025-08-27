from odoo import models, fields


class UtmSource(models.Model):
    _inherit = "utm.source"
    name = fields.Char(translate=False)
