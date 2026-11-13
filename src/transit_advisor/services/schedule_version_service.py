from datetime import datetime

from sqlalchemy.exc import IntegrityError

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

    def create_version(self, checksum: str) -> ScheduleVersion | None:
        existing = self._repository.find_by_checksum(checksum)
        if existing is not None:
            return None
        try:
            return self._repository.save(
                ScheduleVersion(id=None, checksum=checksum, imported_at=datetime.now())
            )
        except IntegrityError:
            return None  # паралельний запит вставив ту саму версію
