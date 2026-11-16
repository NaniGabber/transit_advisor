import json
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from transit_advisor.infrastructure.database.models.agency import AgencyModel
from transit_advisor.infrastructure.database.models.scheduleversion import (
    ScheduleVersionModel,
)


def test_database_snapshot_export_and_import_round_trip(
    client: TestClient,
    session: Session,
) -> None:
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
