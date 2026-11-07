import pytest

from transit_advisor.domain.stoptime import StopTime
from transit_advisor.infrastructure.repositories.stoptime import (
    SqlAlchemyStopTimeRepository,
)


def make_stop_time(
    trip_id: int,
    arrival_time: str,
    departure_time: str,
    stop_id: int = 1,
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
) -> None:
    saved = stoptime_repository.save(
        make_stop_time(
            trip_id=1,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )

    assert saved.id is not None


def test_save_persists_all_fields(
    stoptime_repository: SqlAlchemyStopTimeRepository,
) -> None:
    saved = stoptime_repository.save(
        make_stop_time(
            trip_id=1,
            stop_id=2,
            arrival_time="08:00:00",
            departure_time="08:01:00",
            stop_sequence=3,
        )
    )

    found = stoptime_repository.find_by_trip_id(1)

    assert len(found) == 1
    assert found[0].id == saved.id
    assert found[0].trip_id == 1
    assert found[0].stop_id == 2
    assert found[0].arrival_time == "08:00:00"
    assert found[0].departure_time == "08:01:00"
    assert found[0].stop_sequence == 3


def test_find_by_trip_id_returns_empty_list_when_no_matches(
    stoptime_repository: SqlAlchemyStopTimeRepository,
) -> None:
    found = stoptime_repository.find_by_trip_id(999)

    assert found == []


def test_find_by_trip_id_returns_only_matching_trip(
    stoptime_repository: SqlAlchemyStopTimeRepository,
) -> None:
    stoptime_repository.save(
        make_stop_time(
            trip_id=1,
            arrival_time="08:00:00",
            departure_time="08:01:00",
        )
    )
    stoptime_repository.save(
        make_stop_time(
            trip_id=2,
            arrival_time="09:00:00",
            departure_time="09:01:00",
        )
    )

    found = stoptime_repository.find_by_trip_id(1)

    assert len(found) == 1
    assert found[0].trip_id == 1


def test_find_by_trip_id_orders_by_stop_sequence(
    stoptime_repository: SqlAlchemyStopTimeRepository,
) -> None:
    stoptime_repository.save(
        make_stop_time(
            trip_id=1,
            stop_id=2,
            arrival_time="08:10:00",
            departure_time="08:11:00",
            stop_sequence=2,
        )
    )
    stoptime_repository.save(
        make_stop_time(
            trip_id=1,
            stop_id=1,
            arrival_time="08:00:00",
            departure_time="08:01:00",
            stop_sequence=1,
        )
    )
    stoptime_repository.save(
        make_stop_time(
            trip_id=1,
            stop_id=3,
            arrival_time="08:20:00",
            departure_time="08:21:00",
            stop_sequence=3,
        )
    )

    found = stoptime_repository.find_by_trip_id(1)

    assert [st.stop_sequence for st in found] == [1, 2, 3]
    assert [st.stop_id for st in found] == [1, 2, 3]


def test_save_multiple_stop_times_for_same_trip(
    stoptime_repository: SqlAlchemyStopTimeRepository,
) -> None:
    first = stoptime_repository.save(
        make_stop_time(
            trip_id=1,
            stop_id=1,
            arrival_time="08:00:00",
            departure_time="08:01:00",
            stop_sequence=1,
        )
    )
    second = stoptime_repository.save(
        make_stop_time(
            trip_id=1,
            stop_id=2,
            arrival_time="08:10:00",
            departure_time="08:11:00",
            stop_sequence=2,
        )
    )

    assert first.id is not None
    assert second.id is not None
    assert first.id != second.id

    found = stoptime_repository.find_by_trip_id(1)

    assert len(found) == 2
    assert {st.id for st in found} == {first.id, second.id}


def test_save_rejects_invalid_trip_id(
    stoptime_repository: SqlAlchemyStopTimeRepository,
) -> None:
    with pytest.raises(ValueError):
        stoptime_repository.save(
            StopTime(
                id=None,
                trip_id=0,
                stop_id=1,
                arrival_time="08:00:00",
                departure_time="08:01:00",
                stop_sequence=1,
            )
        )


def test_save_rejects_empty_arrival_time(
    stoptime_repository: SqlAlchemyStopTimeRepository,
) -> None:
    with pytest.raises(ValueError):
        stoptime_repository.save(
            StopTime(
                id=None,
                trip_id=1,
                stop_id=1,
                arrival_time="   ",
                departure_time="08:01:00",
                stop_sequence=1,
            )
        )
