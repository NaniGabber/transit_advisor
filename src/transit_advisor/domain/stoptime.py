from dataclasses import dataclass


@dataclass(slots=True)
class StopTime:
    id: int | None

    trip_id: int
    stop_id: int

    arrival_time: str
    departure_time: str

    stop_sequence: int

    def __post_init__(self) -> None:
        if self.trip_id <= 0:
            raise ValueError("trip_id must be positive")

        if self.stop_id <= 0:
            raise ValueError("stop_id must be positive")

        if not self.arrival_time.strip():
            raise ValueError("arrival time cannot be empty")

        if not self.departure_time.strip():
            raise ValueError("departure time cannot be empty")

        if self.stop_sequence <= 0:
            raise ValueError("stop sequence must be positive")

    @property
    def is_first_stop(self) -> bool:
        return self.stop_sequence == 1
