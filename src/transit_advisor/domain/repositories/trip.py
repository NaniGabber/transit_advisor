from typing import Protocol

from transit_advisor.domain.trip import Trip


class TripRepository(Protocol):
    def save(
        self,
        trip: Trip,
    ) -> Trip: ...

    def find_by_trip_id(
        self,
        trip_id: str,
    ) -> Trip | None: ...
