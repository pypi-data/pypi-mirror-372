# Copyright 2025 Coopdevs Treball SCCL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    """
    Archive duplicated product templates that do not have any XML ID
    and do not have any product variants.
    """

    xml_ids = env["ir.model.data"].search(
        [("model", "=", "product.template"), ("module", "=", "somconnexio")]
    )
    template_ids_with_xml = xml_ids.mapped("res_id")

    ProductTemplate = env["product.template"]

    templates = ProductTemplate.search([("default_code", "!=", False)])

    code_to_templates = defaultdict(set)
    for template in templates:
        code_to_templates[template.default_code].add(template.id)

    duplicated_template_ids = set()
    for template_ids in code_to_templates.values():
        if len(template_ids) > 1:
            duplicated_template_ids.update(template_ids)

    duplicated_templates = ProductTemplate.browse(duplicated_template_ids)
    old_product_templates = duplicated_templates.filtered(
        lambda t: t.id not in template_ids_with_xml
        and t.active
        and not any(t.product_variant_ids.filtered(lambda p: p.active))
    )

    for template in old_product_templates:
        template.write(
            {
                "active": False,
            }
        )
        _logger.info(
            "Archived template with id %s and default_code %s"
            % (template.id, template.default_code)
        )
