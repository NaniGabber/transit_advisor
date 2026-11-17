import logging
from datetime import UTC, datetime

from transit_advisor.domain.exceptions import DuplicateScheduleVersionError
from transit_advisor.domain.repositories.scheduleversion import (
    ScheduleVersionRepository,
)
from transit_advisor.domain.scheduleversion import ScheduleVersion

logger = logging.getLogger(__name__)


class ScheduleVersionService:
    def __init__(self, repository: ScheduleVersionRepository) -> None:
        self._repository = repository

    def create_version(self, checksum: str) -> ScheduleVersion | None:
        existing = self._repository.find_by_checksum(checksum)
        if existing is not None:
            logger.warning(
                "schedule_version_duplicate checksum=%s version_id=%s",
                checksum,
                existing.id,
            )
            return None
        try:
            version = self._repository.save(
                ScheduleVersion(
                    id=None,
                    checksum=checksum,
                    imported_at=datetime.now(UTC),
                )
            )
            logger.info(
                "schedule_version_created version_id=%s checksum=%s",
                version.id,
                checksum,
            )
            return version
        except DuplicateScheduleVersionError:
            logger.warning("schedule_version_duplicate checksum=%s", checksum)
            return None

    def find_latest(self) -> ScheduleVersion | None:
        return self._repository.find_latest()
