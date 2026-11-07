from transit_advisor.infrastructure.gtfs.mappers.trip import (
    to_trip,
)


def test_to_trip_returns_trip_for_valid_row() -> None:
    row = {
        "trip_id": "trip_001",
        "trip_headsign": "City Center",
    }

    trip = to_trip(
        row=row,
        route_id=1,
        schedule_version_id=1,
    )

    assert trip is not None
    assert trip.trip_id == "trip_001"
    assert trip.headsign == "City Center"
    assert trip.schedule_version_id == 1


def test_to_trip_allows_empty_headsign() -> None:
    row = {
        "trip_id": "trip_001",
        "trip_headsign": "",
    }

    trip = to_trip(
        row=row,
        route_id=1,
        schedule_version_id=1,
    )

    assert trip is not None
    assert trip.headsign is None


def test_to_trip_normalizes_headsign() -> None:
    row = {
        "trip_id": "trip_001",
        "trip_headsign": "   City    Center   ",
    }

    trip = to_trip(
        row=row,
        route_id=1,
        schedule_version_id=1,
    )

    assert trip is not None
    assert trip.headsign == "City Center"


def test_to_trip_allows_missing_headsign() -> None:
    row = {
        "trip_id": "trip_001",
        "trip_headsign": None,
    }

    trip = to_trip(
        row=row,
        route_id=1,
        schedule_version_id=1,
    )

    assert trip is not None
    assert trip.headsign is None


def test_to_trip_returns_none_for_empty_trip_id() -> None:
    row = {
        "trip_id": "",
        "trip_headsign": "City Center",
    }

    trip = to_trip(
        row=row,
        route_id=1,
        schedule_version_id=1,
    )

    assert trip is None
