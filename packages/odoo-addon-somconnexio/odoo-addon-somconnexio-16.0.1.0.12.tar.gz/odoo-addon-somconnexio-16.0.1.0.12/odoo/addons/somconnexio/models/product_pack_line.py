from odoo import models


class ProductPackLine(models.Model):
    _inherit = "product.pack.line"

    # disable original sql constrain product_uniq
    _sql_constraints = [
        (
            "product_uniq",
            "Check(1=1)",
            "Product must be only once on a pack!",
        ),
    ]
