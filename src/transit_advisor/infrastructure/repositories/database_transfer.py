from datetime import datetime

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session
from sqlalchemy.sql.schema import Table

from transit_advisor.domain.exceptions import InvalidDatabaseSnapshotError
from transit_advisor.domain.repositories.database_transfer import DatabaseRows
from transit_advisor.infrastructure.database.base import Base


class SqlAlchemyDatabaseTransferRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def table_names(self) -> frozenset[str]:
        return frozenset(table.name for table in Base.metadata.sorted_tables)

    def export_tables(self) -> DatabaseRows:
        return {
            table.name: [
                dict(row) for row in self._session.execute(select(table)).mappings()
            ]
            for table in Base.metadata.sorted_tables
        }

    def replace_tables(self, tables: DatabaseRows) -> dict[str, int]:
        ordered_tables = list(Base.metadata.sorted_tables)
        expected_tables = {table.name for table in ordered_tables}
        if set(tables) != expected_tables:
            raise InvalidDatabaseSnapshotError("Snapshot table set does not match")

        prepared_rows = {
            table.name: self._prepare_rows(table, tables[table.name])
            for table in ordered_tables
        }

        table_list = ", ".join(f'"{table.name}"' for table in reversed(ordered_tables))
        self._session.execute(
            text(f"TRUNCATE TABLE {table_list} RESTART IDENTITY CASCADE")
        )

        for table in ordered_tables:
            rows = prepared_rows[table.name]
            if rows:
                self._session.execute(table.insert(), rows)

        self._reset_sequences(ordered_tables)
        return {name: len(rows) for name, rows in prepared_rows.items()}

    def _prepare_rows(
        self,
        table: Table,
        rows: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        columns = {column.name: column for column in table.columns}
        prepared: list[dict[str, object]] = []

        for row in rows:
            if set(row) != set(columns):
                raise InvalidDatabaseSnapshotError(
                    f"Columns do not match table {table.name}"
                )

            converted: dict[str, object] = {}
            for name, column in columns.items():
                value = row[name]
                if value is None:
                    if not column.nullable:
                        raise InvalidDatabaseSnapshotError(
                            f"Null value in required column {table.name}.{name}"
                        )
                    converted[name] = None
                    continue

                expected_type = column.type.python_type
                if expected_type is datetime:
                    if not isinstance(value, str):
                        raise InvalidDatabaseSnapshotError(
                            f"Invalid datetime in {table.name}.{name}"
                        )
                    try:
                        value = datetime.fromisoformat(value)
                    except ValueError as exc:
                        raise InvalidDatabaseSnapshotError(
                            f"Invalid datetime in {table.name}.{name}"
                        ) from exc
                elif expected_type is int and type(value) is not int:
                    raise InvalidDatabaseSnapshotError(
                        f"Invalid integer in {table.name}.{name}"
                    )
                elif expected_type is float and (type(value) not in (int, float)):
                    raise InvalidDatabaseSnapshotError(
                        f"Invalid number in {table.name}.{name}"
                    )
                elif expected_type is bool and type(value) is not bool:
                    raise InvalidDatabaseSnapshotError(
                        f"Invalid boolean in {table.name}.{name}"
                    )
                elif expected_type is str and not isinstance(value, str):
                    raise InvalidDatabaseSnapshotError(
                        f"Invalid text in {table.name}.{name}"
                    )

                converted[name] = value
            prepared.append(converted)

        return prepared

    def _reset_sequences(self, tables: list[Table]) -> None:
        for table in tables:
            for column in table.primary_key.columns:
                if column.autoincrement is False:
                    continue

                sequence_name = self._session.execute(
                    text("SELECT pg_get_serial_sequence(:table_name, :column_name)"),
                    {"table_name": table.name, "column_name": column.name},
                ).scalar_one_or_none()
                if sequence_name is None:
                    continue

                max_id = self._session.execute(select(func.max(column))).scalar_one()
                if max_id is not None:
                    self._session.execute(
                        text(
                            "SELECT setval(CAST(:sequence_name AS regclass), "
                            ":max_id, true)"
                        ),
                        {"sequence_name": sequence_name, "max_id": max_id},
                    )
