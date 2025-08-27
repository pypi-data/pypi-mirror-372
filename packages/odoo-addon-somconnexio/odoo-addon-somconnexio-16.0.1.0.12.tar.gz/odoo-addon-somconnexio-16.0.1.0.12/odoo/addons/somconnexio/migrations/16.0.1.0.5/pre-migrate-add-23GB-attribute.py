# Copyright 2025 Coopdevs Treball SCCL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    """
    Set no-update to False to Mobile_product_template_Data_attribute_line
    """

    model_data = env["ir.model.data"].search(
        [
            ("name", "=", "Mobile_product_template_Data_attribute_line"),
            ("model", "=", "product.template.attribute.line"),
        ]
    )
    if model_data:
        _logger.info(
            "Setting no_update to False for Mobile_product_template_Data_attribute_line"
        )
        model_data.write({"noupdate": False})
    else:
        _logger.warning(
            "Mobile_product_template_Data_attribute_line not found, skipping update."
        )
