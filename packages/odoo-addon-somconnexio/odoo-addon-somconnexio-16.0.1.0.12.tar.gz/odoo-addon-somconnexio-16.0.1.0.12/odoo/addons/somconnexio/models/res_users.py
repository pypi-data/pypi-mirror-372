from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    chatter_position = fields.Selection(default='bottom')
