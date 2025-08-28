import contextlib

import threading

import select

import time

import logging
from odoo.tools import config, OrderedSet
from odoo import sql_db
from odool.service import db as db_service
import wrapt
from odoo.addons.base.models.ir_cron import ir_cron

SLEEP_INTERVAL = 60  # 1min

_logger = logging.getLogger(__name__)


def cron_database_list():
    return config["db_name"] or db_service.list_dbs(True)


def _run_cron(cr, number):
    pg_conn = cr._cnx
    # LISTEN / NOTIFY doesn't work in recovery mode
    cr.execute("SELECT pg_is_in_recovery()")
    in_recovery = cr.fetchone()[0]
    if not in_recovery:
        cr.execute("LISTEN cron_trigger")
    else:
        _logger.warning("PG cluster in recovery mode, cron trigger not activated")
    cr.commit()
    check_all_time = (
        0.0  # last time that we listed databases, initialized far in the past
    )
    all_db_names = []
    alive_time = time.monotonic()
    while config.get("limit_time_worker_cron", 0) <= 0 or (
        time.monotonic() - alive_time
    ) <= config.get("limit_time_worker_cron", 0):
        select.select([pg_conn], [], [], SLEEP_INTERVAL + number)
        time.sleep(number / 100)
        try:
            pg_conn.poll()
        except Exception:
            if pg_conn.closed:
                # connection closed, just exit the loop
                return
            raise
        notified = OrderedSet(
            notif.payload
            for notif in pg_conn.notifies
            if notif.channel == "cron_trigger"
        )
        pg_conn.notifies.clear()  # free resources

        if time.time() - SLEEP_INTERVAL > check_all_time:
            # check all databases
            # last time we checked them was `now - SLEEP_INTERVAL`
            check_all_time = time.time()
            # process notified databases first, then the other ones
            all_db_names = OrderedSet(cron_database_list())
            db_names = [
                *(db for db in notified if db in all_db_names),
                *(db for db in all_db_names if db not in notified),
            ]
        else:
            # restrict to notified databases only
            db_names = notified.intersection(all_db_names)
            if not db_names:
                continue

        _logger.debug("cron%d polling for jobs (notified: %s)", number, notified)
        for db_name in db_names:
            thread = threading.current_thread()
            thread.start_time = time.time()
            try:
                # noqa: PLC0415 Odoo 19
                ir_cron._process_jobs(db_name)
            except Exception:
                _logger.warning(
                    "cron%d encountered an Exception:", number, exc_info=True
                )
            thread.start_time = None


def _cron_thread_patch(number):
    # Steve Reich timing style with thundering herd mitigation.
    #
    # On startup, all workers bind on a notification channel in
    # postgres so they can be woken up at will. At worst they wake
    # up every SLEEP_INTERVAL with a jitter. The jitter creates a
    # chorus effect that helps distribute on the timeline the moment
    # when individual worker wake up.
    #
    # On NOTIFY, all workers are awaken at the same time, sleeping
    # just a bit prevents they all poll the database at the exact
    # same time. This is known as the thundering herd effect.
    while True:
        conn = sql_db.db_connect("postgres")
        with contextlib.closing(conn.cursor()) as cr:
            _run_cron(cr, number)
            cr._cnx.close()
        _logger.info(
            "cron%d max age (%ss) reached, releasing connection.",
            number,
            config.get("limit_time_worker_cron", 0),
        )


@wrapt.patch_function_wrapper("odoo.service.server", "ThreadedServer.cron_thread")
def _patch_ThreadedServer_cron_thread(wrapped, instance, args, kwargs):
    def _cron_thread_signature(number, *args, **kwargs):
        return number

    return _cron_thread_patch(_cron_thread_signature(*args, **kwargs))
