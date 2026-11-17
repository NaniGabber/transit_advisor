import logging

import pytest

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


def test_missing_agency_file(caplog: pytest.LogCaptureFixture) -> None:
    validator = FeedValidator()

    files = {
        "routes.txt",
        "stops.txt",
        "trips.txt",
        "stop_times.txt",
    }

    with caplog.at_level(
        logging.DEBUG,
        logger="transit_advisor.services.feed_validation_service",
    ):
        is_valid = validator.validate(files)

    assert not is_valid
    assert "feed_validation_completed valid=False" in caplog.text
    assert "agency.txt" in caplog.text


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
