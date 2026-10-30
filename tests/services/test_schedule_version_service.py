from transit_advisor.services.schedule_version_service import (
    ScheduleVersionService,
)

from .fake_repos import FakeScheduleVersionRepository


def test_create_version() -> None:
    repository = FakeScheduleVersionRepository()

    service = ScheduleVersionService(
        repository,
    )

    version = service.create_version(
        "a" * 64,
    )

    assert version is not None
    assert version.id == 1


def test_create_version_saves_version() -> None:
    repository = FakeScheduleVersionRepository()

    service = ScheduleVersionService(
        repository,
    )

    service.create_version(
        "a" * 64,
    )

    assert len(repository.saved) == 1


def test_duplicate_checksum_rejected() -> None:
    repository = FakeScheduleVersionRepository()

    service = ScheduleVersionService(
        repository,
    )

    checksum = "a" * 64

    service.create_version(
        checksum,
    )

    duplicate = service.create_version(
        checksum,
    )

    assert duplicate is None


def test_create_multiple_versions() -> None:
    repository = FakeScheduleVersionRepository()

    service = ScheduleVersionService(
        repository,
    )

    service.create_version(
        "a" * 64,
    )

    service.create_version(
        "b" * 64,
    )

    assert len(repository.saved) == 2
