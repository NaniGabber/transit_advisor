from typing import Protocol

from transit_advisor.domain.trip import Trip


class TripRepository(Protocol):
    def save(
        self,
        trip: Trip,
    ) -> Trip: ...

    def save_all(
        self,
        trips: list[Trip],
    ) -> list[Trip]: ...

    def find_by_trip_id(
        self,
        trip_id: str,
    ) -> Trip | None: ...

    def find_by_trip_ids(
        self,
        trip_ids: list[str],
    ) -> dict[str, Trip]: ...

    def find_by_schedule_version_id(
        self,
        schedule_version_id: int,
    ) -> list[Trip]: ...
