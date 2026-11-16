import hashlib
from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError

from transit_advisor.domain.exceptions import DuplicateScheduleVersionError
from transit_advisor.domain.scheduleversion import ScheduleVersion
from transit_advisor.services.schedule_version_service import (
    ScheduleVersionService,
)

from .fake_repos import FakeScheduleVersionRepository


def _checksum(seed: str) -> str:
    return hashlib.sha256(seed.encode()).hexdigest()


# ---------- існуючі тести ----------


def test_create_version() -> None:
    repository = FakeScheduleVersionRepository()
    service = ScheduleVersionService(repository)

    version = service.create_version("a" * 64)

    assert version is not None
    assert version.id == 1


def test_create_version_saves_version() -> None:
    repository = FakeScheduleVersionRepository()
    service = ScheduleVersionService(repository)

    service.create_version("a" * 64)

    assert len(repository.saved) == 1


def test_duplicate_checksum_rejected() -> None:
    repository = FakeScheduleVersionRepository()
    service = ScheduleVersionService(repository)

    checksum = "a" * 64
    service.create_version(checksum)
    duplicate = service.create_version(checksum)

    assert duplicate is None


def test_create_multiple_versions() -> None:
    repository = FakeScheduleVersionRepository()
    service = ScheduleVersionService(repository)

    service.create_version("a" * 64)
    service.create_version("b" * 64)

    assert len(repository.saved) == 2


# ---------- нові тести ----------


def test_create_version_sets_checksum_and_imported_at() -> None:
    repository = FakeScheduleVersionRepository()
    service = ScheduleVersionService(repository)

    checksum = _checksum("v1")
    before = datetime.now(UTC)
    version = service.create_version(checksum)
    after = datetime.now(UTC)

    assert version is not None
    assert version.checksum == checksum
    assert version.imported_at is not None
    assert before <= version.imported_at <= after


def test_create_version_rejects_invalid_checksum() -> None:
    repository = FakeScheduleVersionRepository()
    service = ScheduleVersionService(repository)

    with pytest.raises(ValueError):
        service.create_version("short")


def test_create_version_rejects_empty_checksum() -> None:
    repository = FakeScheduleVersionRepository()
    service = ScheduleVersionService(repository)

    with pytest.raises(ValueError):
        service.create_version("")


def test_duplicate_does_not_persist_second_version() -> None:
    repository = FakeScheduleVersionRepository()
    service = ScheduleVersionService(repository)

    checksum = _checksum("v1")
    service.create_version(checksum)
    service.create_version(checksum)

    assert len(repository.saved) == 1


def test_duplicate_returns_none_not_existing_version() -> None:
    repository = FakeScheduleVersionRepository()
    service = ScheduleVersionService(repository)

    checksum = _checksum("v1")
    first = service.create_version(checksum)
    second = service.create_version(checksum)

    assert first is not None
    assert second is None


def test_create_version_propagates_unexpected_integrity_error() -> None:
    """Не-UNIQUE IntegrityError не має маскуватися під дублікат."""
    repository = FakeScheduleVersionRepository()
    service = ScheduleVersionService(repository)

    def save_raises_not_null(version: ScheduleVersion) -> ScheduleVersion:
        from sqlalchemy.exc import IntegrityError

        raise IntegrityError(
            "not null violation",
            params=None,
            orig=Exception("null value in column"),
        )

    repository.save = save_raises_not_null  # type: ignore[method-assign]

    with pytest.raises(IntegrityError):
        service.create_version(_checksum("v1"))


def test_create_version_handles_duplicate_on_save() -> None:
    repository = FakeScheduleVersionRepository()
    service = ScheduleVersionService(repository)
    checksum = _checksum("v1")

    with patch.object(
        repository,
        "save",
        side_effect=DuplicateScheduleVersionError(checksum),
    ):
        result = service.create_version(checksum)

    assert result is None


def test_multiple_versions_have_distinct_ids() -> None:
    repository = FakeScheduleVersionRepository()
    service = ScheduleVersionService(repository)

    v1 = service.create_version(_checksum("v1"))
    v2 = service.create_version(_checksum("v2"))

    assert v1 is not None
    assert v2 is not None
    assert v1.id != v2.id


def test_checksum_rejects_uppercase_hex() -> None:
    """SHA-256 hex — lowercase. Uppercase має відхилятися валідацією."""
    repository = FakeScheduleVersionRepository()
    service = ScheduleVersionService(repository)

    with pytest.raises(ValueError):
        service.create_version("A" * 64)

    assert len(repository.saved) == 0
