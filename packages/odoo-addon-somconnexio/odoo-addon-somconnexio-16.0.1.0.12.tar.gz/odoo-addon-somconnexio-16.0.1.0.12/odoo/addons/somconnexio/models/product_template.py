from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    catalog_attribute_id = fields.Many2one(
        "product.attribute.value", "Catalog Product Attribute Value"
    )
    root_categ_id = fields.Many2one(
        "product.category", store=True, compute="_compute_root_categ_id"
    )

    @api.depends("categ_id")
    def _compute_root_categ_id(self):
        for product in self:
            parent_categ = product.categ_id
            while parent_categ.parent_id:
                parent_categ = parent_categ.parent_id
            product.root_categ_id = parent_categ
