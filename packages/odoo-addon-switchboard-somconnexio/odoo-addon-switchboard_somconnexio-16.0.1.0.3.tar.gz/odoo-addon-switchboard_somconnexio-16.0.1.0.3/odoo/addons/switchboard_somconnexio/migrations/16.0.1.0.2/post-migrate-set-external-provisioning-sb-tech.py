# Copyright 2025 Coopdevs Treball SCCL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    sb_technology = env.ref("switchboard_somconnexio.service_technology_switchboard")

    if sb_technology:
        sb_technology.write(
            {
                "external_provisioning_required": True,
            }
        )
        _logger.info(
            """
            Set external_provisioning_required to True
            for service_technology_switchboard.
            """
        )
