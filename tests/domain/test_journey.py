from collections.abc import Callable

import pytest

from tests.services.fake_repos import FakeStopTimeRepository
from transit_advisor.domain.journey import Journey
from transit_advisor.domain.stoptime import StopTime
from transit_advisor.services.journey_service import JourneyService


@pytest.fixture
def make_stop_time() -> Callable[..., StopTime]:
    def create(
        trip_id: int,
        stop_id: int,
        arrival: str,
        departure: str,
        sequence: int,
    ) -> StopTime:
        return StopTime(
            id=None,
            trip_id=trip_id,
            stop_id=stop_id,
            arrival_time=arrival,
            departure_time=departure,
            stop_sequence=sequence,
        )

    return create


@pytest.fixture
def journey_service(
    fake_stoptime_repository: FakeStopTimeRepository,
) -> JourneyService:
    return JourneyService(fake_stoptime_repository)


def test_journey_creation() -> None:
    journey = Journey(
        trip_id=1,
        from_stop_id=10,
        to_stop_id=20,
        departure_time="08:00:00",
        arrival_time="08:10:00",
        stop_sequence_start=1,
        stop_sequence_end=2,
    )

    assert journey.trip_id == 1
    assert journey.from_stop_id == 10
    assert journey.to_stop_id == 20
    assert journey.departure_time == "08:00:00"
    assert journey.arrival_time == "08:10:00"
    assert journey.stop_sequence_start == 1
    assert journey.stop_sequence_end == 2


def test_find_direct_journeys_returns_journey(
    journey_service: JourneyService,
    fake_stoptime_repository: FakeStopTimeRepository,
    make_stop_time: Callable[..., StopTime],
) -> None:
    fake_stoptime_repository.saved.extend(
        [
            make_stop_time(1, 10, "08:00:00", "08:00:00", 1),
            make_stop_time(1, 20, "08:10:00", "08:10:00", 2),
        ]
    )

    journeys = journey_service.find_direct_journeys(from_stop_id=10, to_stop_id=20)

    assert len(journeys) == 1
    assert journeys[0].trip_id == 1
    assert journeys[0].departure_time == "08:00:00"
    assert journeys[0].arrival_time == "08:10:00"


def test_find_direct_journeys_returns_empty_when_no_match(
    journey_service: JourneyService,
    fake_stoptime_repository: FakeStopTimeRepository,
    make_stop_time: Callable[..., StopTime],
) -> None:
    fake_stoptime_repository.saved.append(
        make_stop_time(1, 10, "08:00:00", "08:00:00", 1),
    )

    journeys = journey_service.find_direct_journeys(from_stop_id=10, to_stop_id=99)

    assert journeys == []


def test_find_direct_journeys_ignores_reverse_order(
    journey_service: JourneyService,
    fake_stoptime_repository: FakeStopTimeRepository,
    make_stop_time: Callable[..., StopTime],
) -> None:
    fake_stoptime_repository.saved.extend(
        [
            make_stop_time(1, 10, "08:00:00", "08:00:00", 1),
            make_stop_time(1, 20, "08:10:00", "08:10:00", 2),
        ]
    )

    journeys = journey_service.find_direct_journeys(from_stop_id=20, to_stop_id=10)

    assert journeys == []


def test_find_direct_journeys_sorts_by_departure_time(
    journey_service: JourneyService,
    fake_stoptime_repository: FakeStopTimeRepository,
    make_stop_time: Callable[..., StopTime],
) -> None:
    fake_stoptime_repository.saved.extend(
        [
            make_stop_time(1, 10, "09:00:00", "09:00:00", 1),
            make_stop_time(1, 20, "09:10:00", "09:10:00", 2),
            make_stop_time(2, 10, "08:00:00", "08:00:00", 1),
            make_stop_time(2, 20, "08:10:00", "08:10:00", 2),
        ]
    )

    journeys = journey_service.find_direct_journeys(from_stop_id=10, to_stop_id=20)

    assert len(journeys) == 2
    assert journeys[0].departure_time == "08:00:00"
    assert journeys[1].departure_time == "09:00:00"


def test_find_direct_journeys_applies_pagination(
    journey_service: JourneyService,
    fake_stoptime_repository: FakeStopTimeRepository,
    make_stop_time: Callable[..., StopTime],
) -> None:
    for i in range(5):
        fake_stoptime_repository.saved.extend(
            [
                make_stop_time(i + 1, 10, f"08:0{i}:00", f"08:0{i}:00", 1),
                make_stop_time(i + 1, 20, f"08:1{i}:00", f"08:1{i}:00", 2),
            ]
        )

    journeys = journey_service.find_direct_journeys(
        from_stop_id=10,
        to_stop_id=20,
        limit=2,
        offset=1,
    )

    assert len(journeys) == 2
    assert journeys[0].departure_time == "08:01:00"
    assert journeys[1].departure_time == "08:02:00"
