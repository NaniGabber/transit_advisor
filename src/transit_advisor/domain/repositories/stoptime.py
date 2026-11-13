from datetime import time
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

    def find_by_trip_ids(
        self,
        trip_ids: list[int],
    ) -> list[StopTime]: ...

    def find_by_stop_id(
        self,
        stop_id: int,
    ) -> list[StopTime]: ...

    def find_by_route_id_and_version(
        self,
        route_id: int,
        schedule_version_id: int,
    ) -> list[StopTime]: ...

    def find_departures(
        self,
        stop_id: int,
        from_time: time | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[StopTime]: ...

    def find_direct_journeys(
        self,
        from_stop_id: int,
        to_stop_id: int,
        schedule_version_id: int | None = None,
        from_time: time | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[tuple[StopTime, StopTime]]: ...
