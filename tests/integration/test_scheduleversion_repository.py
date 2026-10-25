from datetime import datetime

from transit_advisor.domain.scheduleversion import (
    ScheduleVersion,
)
from transit_advisor.infrastructure.repositories.scheduleversion import (
    SqlAlchemyScheduleVersionRepository,
)


def test_save_schedule_version(
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
) -> None:
    version = ScheduleVersion(
        id=None,
        checksum="a" * 64,
        imported_at=datetime.now(),
    )

    saved = schedule_version_repository.save(
        version,
    )

    assert saved.id is not None


def test_find_by_checksum(
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
) -> None:
    schedule_version_repository.save(
        ScheduleVersion(
            id=None,
            checksum="a" * 64,
            imported_at=datetime.now(),
        )
    )

    found = schedule_version_repository.find_by_checksum(checksum="a" * 64)

    assert found is not None
    assert found.checksum == "a" * 64


def test_find_by_checksum_returns_none(
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
) -> None:
    found = schedule_version_repository.find_by_checksum(
        "missing",
    )

    assert found is None
