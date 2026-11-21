import logging
import os
import time
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Final

import psycopg
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from transit_advisor.infrastructure.database import models  # noqa: F401
from transit_advisor.infrastructure.database.base import DATABASE_URL
from transit_advisor.infrastructure.repositories.database_transfer import (
    SqlAlchemyDatabaseTransferRepository,
)
from transit_advisor.logging_config import configure_logging
from transit_advisor.services.database_transfer_service import (
    DatabaseTransferService,
)

logger = logging.getLogger(__name__)
BACKUP_INTERVAL_SECONDS: Final = 60 * 60
NOTIFY_CHANNEL: Final = "transit_advisor_backup"
BACKUP_PATH: Final = Path(
    os.environ.get("BACKUP_PATH", "backups/transit-database.json")
)


def _export_snapshot() -> bytes:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    session_factory = sessionmaker(bind=engine, class_=Session)
    try:
        with session_factory() as session:
            service = DatabaseTransferService(
                SqlAlchemyDatabaseTransferRepository(session)
            )
            return service.export_snapshot()
    finally:
        engine.dispose()


def _write_snapshot(path: Path, snapshot: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with NamedTemporaryFile(dir=path.parent, delete=False) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(snapshot)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, path)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise


def _save_snapshot(path: Path) -> None:
    snapshot = _export_snapshot()
    _write_snapshot(path, snapshot)
    logger.info("database_backup_written path=%s bytes=%s", path, len(snapshot))


def run_backup_service() -> None:
    configure_logging()
    database_url = make_url(DATABASE_URL).set(drivername="postgresql")
    connection_string = database_url.render_as_string(hide_password=False)

    with psycopg.connect(connection_string, autocommit=True) as connection:
        connection.execute(f"LISTEN {NOTIFY_CHANNEL}")
        _save_snapshot(BACKUP_PATH)
        next_backup_at = time.monotonic() + BACKUP_INTERVAL_SECONDS
        changed_since_backup = False

        logger.info(
            "database_backup_worker_started path=%s interval_seconds=%s models=%s",
            BACKUP_PATH,
            BACKUP_INTERVAL_SECONDS,
            len(models.__all__),
        )

        while True:
            seconds_until_backup = next_backup_at - time.monotonic()
            if seconds_until_backup > 0:
                notification = next(
                    connection.notifies(
                        timeout=seconds_until_backup,
                        stop_after=1,
                    ),
                    None,
                )
                if notification is not None:
                    changed_since_backup = True
                continue

            if changed_since_backup:
                _save_snapshot(BACKUP_PATH)
                changed_since_backup = False
                next_backup_at = time.monotonic() + BACKUP_INTERVAL_SECONDS
                continue

            logger.info("database_backup_waiting_for_change")
            next(connection.notifies())
            _save_snapshot(BACKUP_PATH)
            next_backup_at = time.monotonic() + BACKUP_INTERVAL_SECONDS


if __name__ == "__main__":
    run_backup_service()
