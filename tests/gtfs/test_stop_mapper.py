import pytest

from transit_advisor.infrastructure.gtfs.mappers.stop import to_stop


def test_to_stop_returns_stop_for_valid_row() -> None:
    row = {
        "stop_id": "stop_1",
        "stop_name": "Central Station",
        "stop_lat": "49.9935",
        "stop_lon": "36.2304",
    }

    stop = to_stop(row)

    assert stop is not None
    assert stop.stop_id == "stop_1"
    assert stop.name == "Central Station"


@pytest.mark.parametrize(
    "row",
    [
        {},
        {
            "stop_name": "Central Station",
            "stop_lat": "49.99",
            "stop_lon": "36.23",
        },
        {
            "stop_id": "stop_1",
            "stop_lat": "49.99",
            "stop_lon": "36.23",
        },
    ],
)
def test_to_stop_returns_none_for_missing_required_fields(
    row: dict[str, str],
) -> None:
    assert to_stop(row) is None


@pytest.mark.parametrize(
    "latitude, longitude",
    [
        ("abc", "36.23"),
        ("49.99", "abc"),
        ("", "36.23"),
        ("49.99", ""),
    ],
)
def test_to_stop_returns_none_for_invalid_coordinates(
    latitude: str,
    longitude: str,
) -> None:
    row = {
        "stop_id": "stop_1",
        "stop_name": "Central Station",
        "stop_lat": latitude,
        "stop_lon": longitude,
    }

    assert to_stop(row) is None


def test_to_stop_normalizes_name() -> None:
    row = {
        "stop_id": "stop_1",
        "stop_name": "   Central    Station   ",
        "stop_lat": "49.99",
        "stop_lon": "36.23",
    }

    stop = to_stop(row)

    assert stop is not None
    assert stop.name == "Central Station"
