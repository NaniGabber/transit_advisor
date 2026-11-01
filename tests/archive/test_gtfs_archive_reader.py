from pathlib import Path

import pytest

from transit_advisor.infrastructure.archive.gtfs_archive_reader import (
    GtfsArchiveReader,
)


def test_lists_files(
    archive_path: Path,
) -> None:
    reader = GtfsArchiveReader()

    files = reader.list_files(
        archive_path,
    )

    assert "agency.txt" in files
    assert "routes.txt" in files
    assert "stops.txt" in files


def test_reads_routes_file(
    archive_path: Path,
) -> None:
    reader = GtfsArchiveReader()

    rows = list(
        reader.read_csv(
            archive_path,
            "routes.txt",
        )
    )

    assert len(rows) == 2
    assert rows[0]["route_id"] == "11"
    assert rows[1]["route_id"] == "15"


def test_reads_stops_file(
    archive_path: Path,
) -> None:
    reader = GtfsArchiveReader()

    rows = list(
        reader.read_csv(
            archive_path,
            "stops.txt",
        )
    )

    assert rows[0]["stop_name"] == "Station"
    assert rows[1]["stop_name"] == "Center"


def test_raises_for_missing_file(
    archive_path: Path,
) -> None:
    reader = GtfsArchiveReader()

    with pytest.raises(KeyError):
        list(
            reader.read_csv(
                archive_path,
                "missing.txt",
            )
        )
