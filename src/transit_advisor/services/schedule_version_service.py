from datetime import datetime

from transit_advisor.domain.repositories.scheduleversion import (
    ScheduleVersionRepository,
)
from transit_advisor.domain.scheduleversion import (
    ScheduleVersion,
)


class ScheduleVersionService:
    def __init__(
        self,
        repository: ScheduleVersionRepository,
    ) -> None:
        self._repository = repository

    def create_version(
        self,
        checksum: str,
    ) -> ScheduleVersion | None:
        existing = self._repository.find_by_checksum(
            checksum,
        )

        if existing is not None:
            return None

        return self._repository.save(
            ScheduleVersion(
                id=None,
                checksum=checksum,
                imported_at=datetime.now(),
            )
        )
