from odoo import models, fields


class XolnProject(models.Model):
    _name = "xoln.project"
    _description = "project to xoln contract info"
    name = fields.Char("Name")
    code = fields.Char("Code")
