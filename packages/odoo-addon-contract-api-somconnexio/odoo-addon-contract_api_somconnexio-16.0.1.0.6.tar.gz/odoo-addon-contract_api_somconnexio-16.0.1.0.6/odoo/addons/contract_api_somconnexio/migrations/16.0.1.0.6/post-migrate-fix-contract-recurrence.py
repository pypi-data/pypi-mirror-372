# Copyright 2025 Coopdevs Treball SCCL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("Migrating contract recurrence settings")
    # Set line_recurrence to True for all contracts that do not have it set
    contract_without_line_recurrence = env["contract.contract"].search(
        [("line_recurrence", "=", False)]
    )
    contract_without_line_recurrence.write(
        {
            "line_recurrence": True,
        }
    )
    _logger.info("Migration done")
