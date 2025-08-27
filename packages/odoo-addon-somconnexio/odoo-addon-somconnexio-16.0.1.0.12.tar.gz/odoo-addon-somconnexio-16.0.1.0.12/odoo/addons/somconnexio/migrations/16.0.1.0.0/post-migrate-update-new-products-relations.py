# Copyright 2025 Coopdevs Treball SCCL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)

models_to_migrate = [
    ("account_analytic_distribution_model", "product_id"),
    ("account_analytic_line", "product_id"),
    ("contract_address_change_wizard", "product_id"),
    ("contract_contract", "current_tariff_product"),
    ("contract_holder_change_wizard", "product_id"),
    ("contract_line", "product_id"),
    ("contract_one_shot_request_wizard", "one_shot_product_id"),
    ("contract_tariff_change_wizard", "new_tariff_product_id"),
    ("contract_template_line", "product_id"),
    ("crm_lead_add_mobile_line_wizard", "product_id"),
    ("crm_lead_line", "product_id"),
    ("operation_request", "share_product_id"),
    ("operation_request", "share_to_product_id"),
    ("partner_create_lead_wizard", "product_id"),
    ("partner_create_subscription", "share_product"),
    ("product_pricelist_item", "product_id"),
    ("product_publish", "product_id"),
    ("product_replenish", "product_id"),
    ("product_supplierinfo", "product_id"),
    ("product_unpublish", "product_id"),
    ("res_config_settings", "deposit_default_product_id"),
    ("sale_advance_payment_inv", "product_id"),
    ("sale_order_line", "product_id"),
    ("sale_order_option", "product_id"),
    ("sale_order_template_line", "product_id"),
    ("sale_order_template_option", "product_id"),
    ("share_line", "share_product_id"),
    ("subscription_register", "share_product_id"),
    ("subscription_register", "share_to_product_id"),
    ("subscription_request", "share_product_id"),
    ("subscription_upgrade_sponsee", "share_product_id"),
]
models_to_migrate_with_sql = [
    ("account_move_line", "product_id"),
    ("product_pack_line", "parent_product_id"),
    ("product_pack_line", "product_id"),
    ("product_variant_combination", "product_product_id"),
]


def migrate_product(env, old_product, new_product):
    _logger.info("migrating product %s", old_product.display_name)
    for model_name, field_name in models_to_migrate:
        _logger.info("    Migrating %s.%s", model_name, field_name)
        model_name = model_name.replace("_", ".")
        try:
            models = env[model_name].search(
                [(field_name, "=", old_product.id), ("active", "in", [True, False])]
            )
        except Exception:
            models = env[model_name].search([(field_name, "=", old_product.id)])
        models.write({field_name: new_product.id})
    for model_name, field_name in models_to_migrate_with_sql:
        _logger.info("    Migrating with SQL %s.%s", model_name, field_name)

        result = env.cr.execute(
            f"SELECT {field_name} FROM {model_name} WHERE {field_name}={old_product.id}"
        )
        result = env.cr.fetchall()
        if not result:
            continue
        env.cr.execute(
            f"UPDATE {model_name} SET {field_name}={new_product.id} WHERE {field_name}={old_product.id}"  # noqa
        )
    _logger.info("Migrated product %s", old_product.display_name)


def get_new_product(env, old_product):
    new_default_code = old_product.default_code.replace("mig12-", "")
    new_product = env["product.product"].search(
        [("default_code", "=", new_default_code)], limit=1
    )
    return new_product


@openupgrade.migrate()
def migrate(env, version):
    old_products = env["product.product"].search(
        [("default_code", "like", "mig12-%"), ("active", "in", [True, False])]
    )
    for old_product in old_products:
        new_product = get_new_product(env, old_product)
        if not new_product:
            _logger.info(
                f"    Product {old_product.display_name} don't have a new equivalent"
            )
            continue
        migrate_product(env, old_product, new_product)
        new_product.write({"public": old_product.public})
        old_product.write(
            {
                "active": False,
                "public": False,
            }
        )
