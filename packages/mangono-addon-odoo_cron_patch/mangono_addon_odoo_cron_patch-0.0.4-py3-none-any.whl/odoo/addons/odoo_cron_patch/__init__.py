import logging
import wrapt

import odoo
from .cron_patch import cron_thread_patched  # noqa

_logger = logging.getLogger(__name__)


def post_load_module():
    if odoo.release.version >= "15.0":
        _logger.info("Enable backport of ThreadedServer.cron_thread")

        @wrapt.patch_function_wrapper("odoo.service.server", "ThreadedServer.cron_thread")
        def _patch_ThreadedServer_cron_thread(wrapped, instance, args, kwargs):
            def _get_number(number, *args, **kwargs):
                return number

            return cron_thread_patched(_get_number(*args, **kwargs))
    else:
        _logger.info("backport of ThreadedServer.cron_thread only available for odoo version from 15.0")
