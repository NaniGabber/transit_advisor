# src/transit_advisor/domain/route.py

from dataclasses import dataclass


@dataclass(slots=True)
class Route:
    id: int | None

    agency_id: int

    route_id: str
    short_name: str
    long_name: str

    route_type: int

    description: str | None = None
    color: str | None = None
    text_color: str | None = None

    def __post_init__(self) -> None:
        if self.agency_id <= 0:
            raise ValueError("agency_id must be positive")

        if not self.route_id.strip():
            raise ValueError("route_id cannot be empty")

        if not self.short_name.strip():
            raise ValueError("route short name cannot be empty")

        if len(self.route_id) > 100:
            raise ValueError("route_id is too long")

        if len(self.short_name) > 50:
            raise ValueError("route short name is too long")

        if len(self.long_name) > 255:
            raise ValueError("route long name is too long")

        if self.route_type < 0:
            raise ValueError("route type cannot be negative")

    @property
    def display_name(self) -> str:
        return f"{self.short_name} {self.long_name}".strip()

    @property
    def is_bus(self) -> bool:
        return self.route_type == 3

    @property
    def is_tram(self) -> bool:
        return self.route_type == 0

    @property
    def is_subway(self) -> bool:
        return self.route_type == 1
