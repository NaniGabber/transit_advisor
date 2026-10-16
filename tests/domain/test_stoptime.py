import pytest

from transit_advisor.domain.stoptime import StopTime


@pytest.mark.parametrize(
    "trip_id, stop_id, arrival_time, departure_time, stop_sequence",
    [
        (0, 1, "08:00:00", "08:01:00", 1),
        (1, 0, "08:00:00", "08:01:00", 1),
        (1, 1, "", "08:01:00", 1),
        (1, 1, "08:00:00", "", 1),
        (1, 1, "08:00:00", "08:01:00", 0),
    ],
)
def test_invalid_stop_time_rejected(
    trip_id: int,
    stop_id: int,
    arrival_time: str,
    departure_time: str,
    stop_sequence: int,
) -> None:
    with pytest.raises(ValueError):
        StopTime(
            id=None,
            trip_id=trip_id,
            stop_id=stop_id,
            arrival_time=arrival_time,
            departure_time=departure_time,
            stop_sequence=stop_sequence,
        )
