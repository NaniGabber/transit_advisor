from __future__ import annotations

from collections.abc import Generator, Iterator
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from transit_advisor.services import backup_service
from transit_advisor.services.backup_service import _write_snapshot


def test_write_snapshot_creates_directory_and_overwrites_previous_file(
    tmp_path: Path,
) -> None:
    backup_path = tmp_path / "backups" / "transit-database.json"
    backup_path.parent.mkdir()
    backup_path.write_bytes(b"old snapshot")

    _write_snapshot(backup_path, b"new snapshot")

    assert backup_path.read_bytes() == b"new snapshot"
    assert list(backup_path.parent.iterdir()) == [backup_path]


def test_worker_backs_up_immediately_after_change_when_hour_was_idle(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class Clock:
        current = 0.0

        def monotonic(self) -> float:
            return self.current

    class Connection:
        waited_for_change = False

        def execute(self, query: str) -> None:
            assert query == "LISTEN transit_advisor_backup"

        def notifies(
            self,
            timeout: float | None = None,
            stop_after: int | None = None,
        ) -> Iterator[object]:
            if timeout is not None:
                assert stop_after == 1
                clock.current += timeout
                return iter(())

            self.waited_for_change = True
            return iter((object(),))

    clock = Clock()
    connection = Connection()
    backup_path = tmp_path / "transit-database.json"
    saved_paths: list[Path] = []

    class StopWorker(Exception):
        pass

    @contextmanager
    def connect(
        connection_string: str,
        *,
        autocommit: bool,
    ) -> Generator[Connection, None, None]:
        assert connection_string.startswith("postgresql://")
        assert autocommit
        yield connection

    def save_snapshot(path: Path) -> None:
        saved_paths.append(path)
        if len(saved_paths) == 2:
            raise StopWorker

    monkeypatch.setattr(
        "transit_advisor.services.backup_service.psycopg.connect",
        connect,
    )
    monkeypatch.setattr(
        backup_service,
        "BACKUP_INTERVAL_SECONDS",
        60 * 60,
    )
    monkeypatch.setattr(
        backup_service,
        "BACKUP_PATH",
        backup_path,
    )
    monkeypatch.setattr(
        backup_service,
        "_save_snapshot",
        save_snapshot,
    )
    monkeypatch.setattr(
        backup_service,
        "time",
        SimpleNamespace(monotonic=clock.monotonic),
    )

    with pytest.raises(StopWorker):
        backup_service.run_backup_service()

    assert saved_paths == [backup_path, backup_path]
    assert connection.waited_for_change
