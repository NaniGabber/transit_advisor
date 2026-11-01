import csv
import zipfile
from collections.abc import Iterator
from pathlib import Path


class GtfsArchiveReader:
    def list_files(
        self,
        archive_path: Path,
    ) -> set[str]:
        with zipfile.ZipFile(archive_path) as archive:
            return set(archive.namelist())

    def read_csv(
        self,
        archive_path: Path,
        file_name: str,
    ) -> Iterator[dict[str, str]]:
        with zipfile.ZipFile(archive_path) as archive:
            with archive.open(file_name) as file:
                rows = (line.decode("utf-8") for line in file)

                reader = csv.DictReader(rows)

                yield from reader

    def exists(
        self,
        archive_path: Path,
        file_name: str,
    ) -> bool:
        with zipfile.ZipFile(archive_path) as archive:
            return file_name in archive.namelist()
