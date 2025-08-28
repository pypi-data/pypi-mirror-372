import logging

import odoo

_logger = logging.getLogger(__name__)


def post_load_module():
    if "15.0" <= odoo.release.version <= "18.0":
        _logger.info("Enable backport of ThreadedServer.cron_thread")
        from . import _wrapt_patcher  # noqa
    else:
        _logger.info(
            "backport of ThreadedServer.cron_thread only available for odoo version from 15.0 until 18.0"
        )
