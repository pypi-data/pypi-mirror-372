# Copyright 2025 Coopdevs Treball SCCL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    sb_old_product_model_data = env["ir.model.data"].search(
        [
            ("module", "=", "switchboard_somconnexio"),
            ("model", "=", "product.product"),
        ]
    )

    # Update the default code of old products
    for model_data in sb_old_product_model_data:
        old_product = env["product.product"].browse(model_data.res_id)
        old_product.write({"default_code": "mig12-sb-" + old_product.default_code})

    sb_old_product_templates_model_data = env["ir.model.data"].search(
        [
            ("module", "=", "switchboard_somconnexio"),
            ("model", "=", "product.template"),
        ]
    )

    _logger.info("Clean DB of old Switchboard products related tables")

    env.cr.execute(
        """
        DELETE FROM product_variant_combination
        WHERE product_product_id = ANY(%s)
    """,
        (sb_old_product_model_data.mapped("res_id"),),
    )

    env.cr.execute(
        """
        DELETE FROM product_template_attribute_value
        WHERE product_tmpl_id = ANY(%s)
    """,
        (sb_old_product_templates_model_data.mapped("res_id"),),
    )

    env.cr.execute(
        """
        DELETE FROM product_template_attribute_line
        WHERE product_tmpl_id = ANY(%s)
    """,
        (sb_old_product_templates_model_data.mapped("res_id"),),
    )

    _logger.info("Unlinking old Switchboard products and templates")

    sb_old_product_model_data.unlink()
    sb_old_product_templates_model_data.unlink()

    _logger.info("Pre migration of old Switchboard products and templates completed")
