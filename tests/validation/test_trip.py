import pytest

from transit_advisor.domain.trip import Trip


@pytest.mark.parametrize(
    "route_id, trip_id",
    [
        (0, "trip-1"),
        (-1, "trip-1"),
        (1, ""),
    ],
)
def test_invalid_trip_rejected(
    route_id: int,
    trip_id: str,
) -> None:
    with pytest.raises(ValueError):
        Trip(
            id=None,
            route_id=route_id,
            trip_id=trip_id,
        )
