import json
from datetime import datetime

import pytest

from transit_advisor.domain.exceptions import InvalidDatabaseSnapshotError
from transit_advisor.domain.repositories.database_transfer import DatabaseRows
from transit_advisor.services.database_transfer_service import (
    SNAPSHOT_FORMAT,
    SNAPSHOT_VERSION,
    DatabaseTransferService,
)


class InMemoryDatabaseTransferRepository:
    def __init__(self) -> None:
        self.tables: DatabaseRows = {"agencies": []}
        self.replaced: DatabaseRows | None = None

    def table_names(self) -> frozenset[str]:
        return frozenset(self.tables)

    def export_tables(self) -> DatabaseRows:
        return self.tables

    def replace_tables(self, tables: DatabaseRows) -> dict[str, int]:
        self.replaced = tables
        return {name: len(rows) for name, rows in tables.items()}


def _snapshot(**overrides: object) -> bytes:
    snapshot: dict[str, object] = {
        "format": SNAPSHOT_FORMAT,
        "version": SNAPSHOT_VERSION,
        "created_at": "2026-01-01T00:00:00+00:00",
        "tables": {"agencies": []},
    }
    snapshot.update(overrides)
    return json.dumps(snapshot).encode("utf-8")


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        pytest.param(b"not json", "valid JSON", id="malformed-json"),
        pytest.param(b"\xff", "valid JSON", id="invalid-utf8"),
        pytest.param(b"[]", "JSON object", id="not-an-object"),
        pytest.param(_snapshot(format="other"), "format", id="wrong-format"),
        pytest.param(_snapshot(version=True), "version", id="boolean-version"),
        pytest.param(_snapshot(version=2), "version", id="unsupported-version"),
        pytest.param(_snapshot(created_at=None), "created_at", id="missing-date"),
        pytest.param(_snapshot(tables=None), "table data", id="missing-tables"),
        pytest.param(
            _snapshot(tables={"unknown": []}),
            "table set",
            id="table-set-mismatch",
        ),
        pytest.param(
            _snapshot(tables={"agencies": {}}),
            "rows are invalid",
            id="rows-not-a-list",
        ),
        pytest.param(
            _snapshot(tables={"agencies": ["not a row"]}),
            "rows are invalid",
            id="row-not-an-object",
        ),
    ],
)
def test_import_snapshot_rejects_invalid_envelopes(
    payload: bytes,
    error: str,
) -> None:
    repository = InMemoryDatabaseTransferRepository()
    service = DatabaseTransferService(repository)

    with pytest.raises(InvalidDatabaseSnapshotError, match=error):
        service.import_snapshot(payload)

    assert repository.replaced is None


def test_export_snapshot_serializes_datetime_values() -> None:
    repository = InMemoryDatabaseTransferRepository()
    repository.tables = {"agencies": [{"created_at": datetime(2026, 1, 1)}]}

    snapshot = json.loads(DatabaseTransferService(repository).export_snapshot())

    assert snapshot["format"] == SNAPSHOT_FORMAT
    assert snapshot["version"] == SNAPSHOT_VERSION
    assert snapshot["tables"]["agencies"][0]["created_at"] == "2026-01-01T00:00:00"


def test_export_snapshot_rejects_unsupported_values() -> None:
    repository = InMemoryDatabaseTransferRepository()
    repository.tables = {"agencies": [{"unsupported": object()}]}

    with pytest.raises(TypeError, match="Unsupported snapshot value"):
        DatabaseTransferService(repository).export_snapshot()


def test_import_snapshot_passes_valid_tables_to_repository() -> None:
    repository = InMemoryDatabaseTransferRepository()
    service = DatabaseTransferService(repository)
    tables = {"agencies": [{"id": 1}]}

    imported = service.import_snapshot(_snapshot(tables=tables))

    assert imported == {"agencies": 1}
    assert repository.replaced == tables
