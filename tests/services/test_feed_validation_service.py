from transit_advisor.services.feed_validation_service import (
    FeedValidator,
)


def test_valid_archive() -> None:
    validator = FeedValidator()

    files = {
        "agency.txt",
        "routes.txt",
        "stops.txt",
        "trips.txt",
        "stop_times.txt",
    }

    assert validator.validate(files)


def test_missing_agency_file() -> None:
    validator = FeedValidator()

    files = {
        "routes.txt",
        "stops.txt",
        "trips.txt",
        "stop_times.txt",
    }

    assert not validator.validate(files)


def test_missing_routes_file() -> None:
    validator = FeedValidator()

    files = {
        "agency.txt",
        "stops.txt",
        "trips.txt",
        "stop_times.txt",
    }

    assert not validator.validate(files)


def test_missing_stop_times_file() -> None:
    validator = FeedValidator()

    files = {
        "agency.txt",
        "routes.txt",
        "stops.txt",
        "trips.txt",
    }

    assert not validator.validate(files)
