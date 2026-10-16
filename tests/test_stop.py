import pytest

from transit_advisor.domain.stop import Stop


@pytest.mark.parametrize(
    "latitude, longitude",
    [
        (-91.0, 30.0),
        (91.0, 30.0),
        (50.0, -181.0),
        (50.0, 181.0),
    ],
)
def test_invalid_coordinates_rejected(
    latitude: float,
    longitude: float,
) -> None:
    with pytest.raises(ValueError):
        Stop(
            id=None,
            stop_id="123",
            name="Central Station",
            latitude=latitude,
            longitude=longitude,
        )
