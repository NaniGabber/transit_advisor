from dataclasses import dataclass


@dataclass(slots=True)
class Trip:
    id: int | None

    route_id: int
    trip_id: str

    headsign: str | None = None

    def __post_init__(self) -> None:
        if self.route_id <= 0:
            raise ValueError("route_id must be positive")

        if not self.trip_id.strip():
            raise ValueError("trip_id cannot be empty")

        if len(self.trip_id) > 100:
            raise ValueError("trip_id is too long")

        if self.headsign is not None and len(self.headsign) > 255:
            raise ValueError("headsign is too long")

    @property
    def has_headsign(self) -> bool:
        return self.headsign is not None and bool(self.headsign.strip())
