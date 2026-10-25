from typing import Protocol

from transit_advisor.domain.scheduleversion import (
    ScheduleVersion,
)


class ScheduleVersionRepository(Protocol):
    def save(
        self,
        version: ScheduleVersion,
    ) -> ScheduleVersion: ...

    def find_by_checksum(
        self,
        checksum: str,
    ) -> ScheduleVersion | None: ...
