import pytest

from transit_advisor.infrastructure.gtfs.mappers.stoptime import (
    to_stoptime,
)


def test_to_stop_time_returns_stop_time_for_valid_row() -> None:
    row = {
        "arrival_time": "08:00:00",
        "departure_time": "08:01:00",
        "stop_sequence": "1",
    }

    stop_time = to_stoptime(
        row=row,
        trip_id=1,
        stop_id=1,
    )

    assert stop_time is not None
    assert stop_time.trip_id == 1
    assert stop_time.stop_id == 1
    assert stop_time.arrival_time == "08:00:00"
    assert stop_time.departure_time == "08:01:00"
    assert stop_time.stop_sequence == 1


@pytest.mark.parametrize(
    "row",
    [
        {},
        {
            "departure_time": "08:01:00",
            "stop_sequence": "1",
        },
        {
            "arrival_time": "08:00:00",
            "stop_sequence": "1",
        },
        {
            "arrival_time": "08:00:00",
            "departure_time": "08:01:00",
        },
    ],
)
def test_to_stop_time_returns_none_for_missing_required_fields(
    row: dict[str, str],
) -> None:
    assert (
        to_stoptime(
            row=row,
            trip_id=1,
            stop_id=1,
        )
        is None
    )


@pytest.mark.parametrize(
    "stop_sequence",
    [
        "",
        "abc",
        "1.5",
    ],
)
def test_to_stop_time_returns_none_for_invalid_stop_sequence(
    stop_sequence: str,
) -> None:
    row = {
        "arrival_time": "08:00:00",
        "departure_time": "08:01:00",
        "stop_sequence": stop_sequence,
    }

    assert (
        to_stoptime(
            row=row,
            trip_id=1,
            stop_id=1,
        )
        is None
    )


def test_to_stop_time_returns_none_for_empty_arrival_time() -> None:
    row = {
        "arrival_time": "",
        "departure_time": "08:01:00",
        "stop_sequence": "1",
    }

    assert (
        to_stoptime(
            row=row,
            trip_id=1,
            stop_id=1,
        )
        is None
    )


def test_to_stop_time_returns_none_for_empty_departure_time() -> None:
    row = {
        "arrival_time": "08:00:00",
        "departure_time": "",
        "stop_sequence": "1",
    }

    assert (
        to_stoptime(
            row=row,
            trip_id=1,
            stop_id=1,
        )
        is None
    )
