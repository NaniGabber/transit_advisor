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
