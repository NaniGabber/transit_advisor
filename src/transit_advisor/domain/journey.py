from dataclasses import dataclass


@dataclass(frozen=True)
class Journey:
    trip_id: int
    from_stop_id: int
    to_stop_id: int
    departure_time: str
    arrival_time: str
    stop_sequence_start: int
    stop_sequence_end: int
