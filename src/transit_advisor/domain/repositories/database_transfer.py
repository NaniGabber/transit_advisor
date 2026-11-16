from typing import Protocol

DatabaseRows = dict[str, list[dict[str, object]]]


class DatabaseTransferRepository(Protocol):
    def table_names(self) -> frozenset[str]: ...

    def export_tables(self) -> DatabaseRows: ...

    def replace_tables(self, tables: DatabaseRows) -> dict[str, int]: ...
