import json
import logging
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Column, Integer, MetaData, Table, text
from sqlalchemy.orm import Session

from transit_advisor.domain.exceptions import InvalidDatabaseSnapshotError
from transit_advisor.infrastructure.database.models.agency import AgencyModel
from transit_advisor.infrastructure.database.models.scheduleversion import (
    ScheduleVersionModel,
)
from transit_advisor.infrastructure.repositories.database_transfer import (
    SqlAlchemyDatabaseTransferRepository,
)


def test_database_snapshot_export_and_import_round_trip(
    client: TestClient,
    session: Session,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(
        logging.INFO,
        logger="transit_advisor.services.database_transfer_service",
    )
    agency = AgencyModel(
        agency_id="metro",
        name="Kharkiv Metro",
        timezone="Europe/Kyiv",
    )
    schedule_version = ScheduleVersionModel(
        checksum="a" * 64,
        imported_at=datetime(2026, 1, 1, 12, 30),
    )
    session.add_all([agency, schedule_version])
    session.commit()
    original_agency_id = agency.id

    exported = client.get(
        "/api/v1/admin/database/export",
        headers={"X-Role": "admin"},
    )

    assert exported.status_code == 200
    assert "attachment; filename=" in exported.headers["content-disposition"]
    snapshot = json.loads(exported.content)
    assert snapshot["format"] == "transit-advisor-database"
    assert snapshot["version"] == 1
    assert snapshot["tables"]["agencies"][0]["agency_id"] == "metro"

    session.add(
        AgencyModel(
            agency_id="temporary",
            name="Temporary Agency",
            timezone="UTC",
        )
    )
    session.commit()

    restored = client.post(
        "/api/v1/admin/database/import",
        headers={"X-Role": "admin"},
        files={"file": ("backup.json", exported.content, "application/json")},
        data={"confirm": "true"},
    )

    assert restored.status_code == 200
    assert restored.json()["imported"]["agencies"] == 1
    assert restored.json()["imported"]["schedule_versions"] == 1
    assert session.query(AgencyModel).count() == 1
    assert session.query(ScheduleVersionModel).one().imported_at == datetime(
        2026,
        1,
        1,
        12,
        30,
    )
    assert "database_snapshot_exported" in caplog.text
    assert "database_snapshot_imported" in caplog.text

    session.add(
        AgencyModel(
            agency_id="after-restore",
            name="After Restore",
            timezone="UTC",
        )
    )
    session.commit()
    assert session.query(AgencyModel).filter_by(agency_id="after-restore").one().id > (
        original_agency_id
    )


def test_database_transfer_is_admin_only(client: TestClient) -> None:
    exported = client.get(
        "/api/v1/admin/database/export",
        headers={"X-Role": "user"},
    )
    imported = client.post(
        "/api/v1/admin/database/import",
        headers={"X-Role": "user"},
        files={"file": ("backup.json", b"{}", "application/json")},
        data={"confirm": "true"},
    )

    assert exported.status_code == 403
    assert imported.status_code == 403


def test_invalid_snapshot_keeps_existing_database_data(
    client: TestClient,
    session: Session,
) -> None:
    session.add(
        AgencyModel(
            agency_id="keep-me",
            name="Existing Agency",
            timezone="UTC",
        )
    )
    session.commit()

    response = client.post(
        "/api/v1/admin/database/import",
        headers={"X-Role": "admin"},
        files={"file": ("broken.json", b"not json", "application/json")},
        data={"confirm": "true"},
    )

    assert response.status_code == 422
    assert session.query(AgencyModel).filter_by(agency_id="keep-me").count() == 1


def test_database_import_requires_confirmation(client: TestClient) -> None:
    response = client.post(
        "/api/v1/admin/database/import",
        headers={"X-Role": "admin"},
        files={"file": ("backup.json", b"{}", "application/json")},
        data={"confirm": "false"},
    )

    assert response.status_code == 400


def test_database_import_rejects_oversized_snapshot(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "transit_advisor.api.database_transfer.MAX_SNAPSHOT_SIZE",
        4,
    )

    response = client.post(
        "/api/v1/admin/database/import",
        headers={"X-Role": "admin"},
        files={"file": ("large.json", b"12345", "application/json")},
        data={"confirm": "true"},
    )

    assert response.status_code == 413


@pytest.mark.parametrize(
    ("table", "row"),
    [
        pytest.param("agencies", {"id": 1}, id="wrong-columns"),
        pytest.param(
            "agencies",
            {
                "id": 1,
                "agency_id": "metro",
                "name": None,
                "timezone": "UTC",
                "language": None,
                "phone": None,
                "fare_url": None,
                "email": None,
            },
            id="null-required-column",
        ),
        pytest.param(
            "agencies",
            {
                "id": "1",
                "agency_id": "metro",
                "name": "Metro",
                "timezone": "UTC",
                "language": None,
                "phone": None,
                "fare_url": None,
                "email": None,
            },
            id="invalid-integer",
        ),
        pytest.param(
            "agencies",
            {
                "id": 1,
                "agency_id": 1,
                "name": "Metro",
                "timezone": "UTC",
                "language": None,
                "phone": None,
                "fare_url": None,
                "email": None,
            },
            id="invalid-text",
        ),
        pytest.param(
            "schedule_versions",
            {"id": 1, "checksum": "a" * 64, "imported_at": 123},
            id="datetime-not-string",
        ),
        pytest.param(
            "schedule_versions",
            {"id": 1, "checksum": "a" * 64, "imported_at": "invalid"},
            id="malformed-datetime",
        ),
        pytest.param(
            "stops",
            {
                "id": 1,
                "stop_id": "S1",
                "name": "Station",
                "latitude": "north",
                "longitude": 36.0,
                "code": None,
                "description": None,
            },
            id="invalid-float",
        ),
        pytest.param(
            "subscriptions",
            {"id": 1, "user_id": 1, "route_id": 1, "is_active": 1},
            id="invalid-boolean",
        ),
    ],
)
def test_database_import_rejects_invalid_row_columns_and_types(
    client: TestClient,
    table: str,
    row: dict[str, object],
) -> None:
    exported = client.get(
        "/api/v1/admin/database/export",
        headers={"X-Role": "admin"},
    )
    snapshot = json.loads(exported.content)
    snapshot["tables"][table] = [row]

    imported = client.post(
        "/api/v1/admin/database/import",
        headers={"X-Role": "admin"},
        files={
            "file": (
                "invalid.json",
                json.dumps(snapshot).encode(),
                "application/json",
            )
        },
        data={"confirm": "true"},
    )

    assert imported.status_code == 422


def test_repository_rejects_mismatched_table_set(
    session: Session,
) -> None:
    repository = SqlAlchemyDatabaseTransferRepository(session)

    with pytest.raises(InvalidDatabaseSnapshotError, match="table set"):
        repository.replace_tables({})


def test_repository_skips_non_autoincrement_primary_key(session: Session) -> None:
    table = Table(
        "manual_ids",
        MetaData(),
        Column("id", Integer, primary_key=True, autoincrement=False),
    )

    SqlAlchemyDatabaseTransferRepository(session)._reset_sequences([table])


def test_repository_skips_primary_key_without_sequence(session: Session) -> None:
    session.execute(
        text("CREATE TEMP TABLE transfer_without_sequence (id INTEGER PRIMARY KEY)")
    )
    table = Table(
        "transfer_without_sequence",
        MetaData(),
        Column("id", Integer, primary_key=True),
    )

    SqlAlchemyDatabaseTransferRepository(session)._reset_sequences([table])
