from collections.abc import Callable
from datetime import time

from transit_advisor.domain.stop import Stop
from transit_advisor.domain.stoptime import StopTime
from transit_advisor.domain.trip import Trip
from transit_advisor.infrastructure.repositories.stoptime import (
    SqlAlchemyStopTimeRepository,
)


def make_stop_time(
    trip_id: int,
    stop_id: int,
    arrival_time: str,
    departure_time: str,
    stop_sequence: int = 1,
) -> StopTime:
    return StopTime(
        id=None,
        trip_id=trip_id,
        stop_id=stop_id,
        arrival_time=arrival_time,
        departure_time=departure_time,
        stop_sequence=stop_sequence,
    )


def test_save_assigns_id(
    stoptime_repository: SqlAlchemyStopTimeRepository,
    trip: Trip,
    stop: Stop,
) -> None:
    assert trip.id is not None
    assert stop.id is not None

    saved = stoptime_repository.save(
        make_stop_time(
            trip_id=trip.id,
            stop_id=stop.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )

    assert saved.id is not None


def test_save_persists_all_fields(
    stoptime_repository: SqlAlchemyStopTimeRepository,
    trip: Trip,
    stop: Stop,
) -> None:
    assert trip.id is not None
    assert stop.id is not None

    saved = stoptime_repository.save(
        make_stop_time(
            trip_id=trip.id,
            stop_id=stop.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
            stop_sequence=3,
        )
    )

    found = stoptime_repository.find_by_trip_id(trip.id)

    assert len(found) == 1
    assert found[0].id == saved.id
    assert found[0].trip_id == trip.id
    assert found[0].stop_id == stop.id
    assert found[0].arrival_time == "08:00:00"
    assert found[0].departure_time == "08:01:00"
    assert found[0].stop_sequence == 3


def test_save_multiple_stop_times_for_same_trip(
    stoptime_repository: SqlAlchemyStopTimeRepository,
    trip: Trip,
    stop_factory: Callable[[str, str], Stop],
) -> None:
    assert trip.id is not None

    stop_1 = stop_factory("stop_1", "Station")
    stop_2 = stop_factory("stop_2", "Center")

    assert stop_1.id is not None
    assert stop_2.id is not None

    first = stoptime_repository.save(
        make_stop_time(
            trip_id=trip.id,
            stop_id=stop_1.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
            stop_sequence=1,
        )
    )
    second = stoptime_repository.save(
        make_stop_time(
            trip_id=trip.id,
            stop_id=stop_2.id,
            arrival_time="08:10:00",
            departure_time="08:11:00",
            stop_sequence=2,
        )
    )

    assert first.id is not None
    assert second.id is not None
    assert first.id != second.id

    found = stoptime_repository.find_by_trip_id(trip.id)

    assert len(found) == 2
    assert {st.id for st in found} == {first.id, second.id}


def test_find_by_trip_id_returns_empty_list_when_no_matches(
    stoptime_repository: SqlAlchemyStopTimeRepository,
) -> None:
    found = stoptime_repository.find_by_trip_id(999)

    assert found == []


def test_find_by_trip_id_returns_only_matching_trip(
    stoptime_repository: SqlAlchemyStopTimeRepository,
    trip: Trip,
    trip_factory: Callable[[str], Trip],
    stop: Stop,
) -> None:
    assert trip.id is not None
    assert stop.id is not None

    other_trip = trip_factory("trip_2")
    assert other_trip.id is not None

    stoptime_repository.save(
        make_stop_time(
            trip_id=trip.id,
            stop_id=stop.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )
    stoptime_repository.save(
        make_stop_time(
            trip_id=other_trip.id,
            stop_id=stop.id,
            arrival_time="09:00:00",
            departure_time="09:01:00",
        )
    )

    found = stoptime_repository.find_by_trip_id(trip.id)

    assert len(found) == 1
    assert found[0].trip_id == trip.id


def test_find_by_trip_id_orders_by_stop_sequence(
    stoptime_repository: SqlAlchemyStopTimeRepository,
    trip: Trip,
    stop_factory: Callable[[str, str], Stop],
) -> None:
    assert trip.id is not None

    stop_1 = stop_factory("stop_1", "Station")
    stop_2 = stop_factory("stop_2", "Center")
    stop_3 = stop_factory("stop_3", "Airport")

    assert stop_1.id is not None
    assert stop_2.id is not None
    assert stop_3.id is not None

    stoptime_repository.save(
        make_stop_time(
            trip_id=trip.id,
            stop_id=stop_2.id,
            arrival_time="08:10:00",
            departure_time="08:11:00",
            stop_sequence=2,
        )
    )
    stoptime_repository.save(
        make_stop_time(
            trip_id=trip.id,
            stop_id=stop_1.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
            stop_sequence=1,
        )
    )
    stoptime_repository.save(
        make_stop_time(
            trip_id=trip.id,
            stop_id=stop_3.id,
            arrival_time="08:20:00",
            departure_time="08:21:00",
            stop_sequence=3,
        )
    )

    found = stoptime_repository.find_by_trip_id(trip.id)

    assert [st.stop_sequence for st in found] == [1, 2, 3]
    assert [st.stop_id for st in found] == [stop_1.id, stop_2.id, stop_3.id]


def test_find_by_trip_ids_returns_empty_for_empty_list(
    stoptime_repository: SqlAlchemyStopTimeRepository,
) -> None:
    assert stoptime_repository.find_by_trip_ids([]) == []


def test_find_by_trip_ids_returns_stop_times_for_multiple_trips(
    stoptime_repository: SqlAlchemyStopTimeRepository,
    trip: Trip,
    trip_factory: Callable[[str], Trip],
    stop: Stop,
) -> None:
    assert trip.id is not None
    assert stop.id is not None

    other_trip = trip_factory("trip_2")
    assert other_trip.id is not None

    stoptime_repository.save(
        make_stop_time(
            trip_id=trip.id,
            stop_id=stop.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )
    stoptime_repository.save(
        make_stop_time(
            trip_id=other_trip.id,
            stop_id=stop.id,
            arrival_time="09:00:00",
            departure_time="09:01:00",
        )
    )

    found = stoptime_repository.find_by_trip_ids([trip.id, other_trip.id])

    assert len(found) == 2
    assert {st.trip_id for st in found} == {trip.id, other_trip.id}


def test_find_by_stop_id_returns_stop_times(
    stoptime_repository: SqlAlchemyStopTimeRepository,
    trip: Trip,
    stop: Stop,
) -> None:
    assert trip.id is not None
    assert stop.id is not None

    stoptime_repository.save(
        make_stop_time(
            trip_id=trip.id,
            stop_id=stop.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )

    found = stoptime_repository.find_by_stop_id(stop.id)

    assert len(found) == 1
    assert found[0].stop_id == stop.id


def test_find_by_stop_id_returns_empty_for_unknown_stop(
    stoptime_repository: SqlAlchemyStopTimeRepository,
) -> None:
    assert stoptime_repository.find_by_stop_id(999) == []


def test_find_departures_filters_by_time(
    stoptime_repository: SqlAlchemyStopTimeRepository,
    trip: Trip,
    stop: Stop,
) -> None:
    assert trip.id is not None
    assert stop.id is not None

    stoptime_repository.save(
        make_stop_time(
            trip_id=trip.id,
            stop_id=stop.id,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )
    stoptime_repository.save(
        make_stop_time(
            trip_id=trip.id,
            stop_id=stop.id,
            arrival_time="10:00:00",
            departure_time="10:01:00",
            stop_sequence=2,
        )
    )

    found = stoptime_repository.find_departures(
        stop_id=stop.id,
        from_time=time(9, 0),
    )

    assert len(found) == 1
    assert found[0].departure_time == "10:01:00"


def test_find_departures_applies_pagination(
    stoptime_repository: SqlAlchemyStopTimeRepository,
    trip: Trip,
    stop: Stop,
) -> None:
    assert trip.id is not None
    assert stop.id is not None

    for hour in range(8, 13):
        stoptime_repository.save(
            make_stop_time(
                trip_id=trip.id,
                stop_id=stop.id,
                arrival_time=f"{hour:02d}:00:00",
                departure_time=f"{hour:02d}:01:00",
                stop_sequence=hour,
            )
        )

    found = stoptime_repository.find_departures(
        stop_id=stop.id,
        from_time=time(8, 0),
        offset=1,
        limit=2,
    )

    assert len(found) == 2
    assert [st.departure_time for st in found] == ["09:01:00", "10:01:00"]
