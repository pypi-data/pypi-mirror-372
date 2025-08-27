# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PartnerActionTag(models.Model):
    _name = "partner.action.tag"

    name = fields.Char(string="Action Tag Name", required=True, translate=True)
    code = fields.Char(string="Code", required=True)
    partner_ids = fields.Many2many(
        "res.partner", column1="action_tag_id", column2="partner_id", string="Partners"
    )
