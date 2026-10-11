# src/transit_advisor/domain/stop.py

from dataclasses import dataclass


@dataclass(slots=True)
class Stop:
    id: int | None

    stop_id: str
    name: str

    latitude: float
    longitude: float

    code: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        if not self.stop_id.strip():
            raise ValueError("stop_id cannot be empty")

        if not self.name.strip():
            raise ValueError("stop name cannot be empty")

        if len(self.stop_id) > 100:
            raise ValueError("stop_id is too long")

        if len(self.name) > 255:
            raise ValueError("stop name is too long")

        if not (-90 <= self.latitude <= 90):
            raise ValueError("latitude must be between -90 and 90")

        if not (-180 <= self.longitude <= 180):
            raise ValueError("longitude must be between -180 and 180")

    @property
    def coordinates(self) -> tuple[float, float]:
        return self.latitude, self.longitude
