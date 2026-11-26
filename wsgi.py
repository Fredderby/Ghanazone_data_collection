"""WSGI entrypoint for Gunicorn / container deployments."""

import logging
import time

from app import app
import db

logger = logging.getLogger(__name__)


def _init_database(attempts=5, delay=3):
    for attempt in range(1, attempts + 1):
        try:
            db.init_db()
            logger.info("Database initialized")
            return
        except Exception as exc:
            logger.warning("Database init attempt %d/%d failed: %s", attempt, attempts, exc)
            if attempt < attempts:
                time.sleep(delay)
    raise RuntimeError("Could not initialize database after %d attempts" % attempts)


_init_database()
