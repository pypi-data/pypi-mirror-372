from odoo import models, fields


class Tag(models.Model):
    _inherit = "crm.tag"
    code = fields.Char("Code")
