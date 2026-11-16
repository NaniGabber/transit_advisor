import json
from datetime import UTC, datetime
from typing import cast

from transit_advisor.domain.exceptions import InvalidDatabaseSnapshotError
from transit_advisor.domain.repositories.database_transfer import (
    DatabaseRows,
    DatabaseTransferRepository,
)

SNAPSHOT_FORMAT = "transit-advisor-database"
SNAPSHOT_VERSION = 1


class DatabaseTransferService:
    def __init__(self, repository: DatabaseTransferRepository) -> None:
        self._repository = repository

    def export_snapshot(self) -> bytes:
        snapshot = {
            "format": SNAPSHOT_FORMAT,
            "version": SNAPSHOT_VERSION,
            "created_at": datetime.now(UTC).isoformat(),
            "tables": self._repository.export_tables(),
        }
        return json.dumps(
            snapshot,
            default=self._serialize_value,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

    def import_snapshot(self, snapshot_bytes: bytes) -> dict[str, int]:
        try:
            snapshot = json.loads(snapshot_bytes)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise InvalidDatabaseSnapshotError("Snapshot is not valid JSON") from exc

        if not isinstance(snapshot, dict):
            raise InvalidDatabaseSnapshotError("Snapshot must be a JSON object")
        if snapshot.get("format") != SNAPSHOT_FORMAT:
            raise InvalidDatabaseSnapshotError("Unsupported snapshot format")
        if type(snapshot.get("version")) is not int or snapshot["version"] != 1:
            raise InvalidDatabaseSnapshotError("Unsupported snapshot version")
        if not isinstance(snapshot.get("created_at"), str):
            raise InvalidDatabaseSnapshotError("Snapshot is missing created_at")

        tables = snapshot.get("tables")
        if not isinstance(tables, dict):
            raise InvalidDatabaseSnapshotError("Snapshot is missing table data")
        if set(tables) != self._repository.table_names():
            raise InvalidDatabaseSnapshotError("Snapshot table set does not match")
        if not all(
            isinstance(rows, list) and all(isinstance(row, dict) for row in rows)
            for rows in tables.values()
        ):
            raise InvalidDatabaseSnapshotError("Snapshot table rows are invalid")

        return self._repository.replace_tables(cast(DatabaseRows, tables))

    @staticmethod
    def _serialize_value(value: object) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        raise TypeError(f"Unsupported snapshot value: {type(value).__name__}")
