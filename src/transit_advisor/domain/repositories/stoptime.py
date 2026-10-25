from typing import Protocol

from transit_advisor.domain.stoptime import StopTime


class StopTimeRepository(Protocol):
    def save(
        self,
        stop_time: StopTime,
    ) -> StopTime: ...

    def find_by_trip_id(
        self,
        trip_id: int,
    ) -> list[StopTime]: ...
