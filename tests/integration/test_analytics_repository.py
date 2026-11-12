from datetime import UTC, datetime

from sqlalchemy.orm import Session

from transit_advisor.domain.agency import Agency
from transit_advisor.domain.route import Route
from transit_advisor.domain.scheduleversion import ScheduleVersion
from transit_advisor.domain.stop import Stop
from transit_advisor.domain.stoptime import StopTime
from transit_advisor.domain.trip import Trip
from transit_advisor.infrastructure.repositories.analytics import (
    SqlAlchemyAnalyticsRepository,
)
from transit_advisor.infrastructure.repositories.route import (
    SqlAlchemyRouteRepository,
)
from transit_advisor.infrastructure.repositories.scheduleversion import (
    SqlAlchemyScheduleVersionRepository,
)
from transit_advisor.infrastructure.repositories.stop import (
    SqlAlchemyStopRepository,
)
from transit_advisor.infrastructure.repositories.stoptime import (
    SqlAlchemyStopTimeRepository,
)
from transit_advisor.infrastructure.repositories.trip import (
    SqlAlchemyTripRepository,
)


def test_count_trips_by_day_returns_empty_when_no_versions(session: Session) -> None:
    repo = SqlAlchemyAnalyticsRepository(session)
    assert repo.count_trips_by_day(1) == {}


def test_count_trips_by_day_returns_counts(
    session: Session,
    agency: Agency,
    route_repository: SqlAlchemyRouteRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    trip_repository: SqlAlchemyTripRepository,
) -> None:
    assert agency.id is not None

    route = route_repository.save(
        Route(
            id=None,
            agency_id=agency.id,
            route_id="1001",
            short_name="1001",
            long_name="Station",
            route_type=3,
        )
    )
    assert route.id is not None

    version = schedule_version_repository.save(
        ScheduleVersion(
            id=None,
            checksum="a" * 64,
            imported_at=datetime.now(UTC),
        )
    )
    assert version.id is not None

    trip_repository.save(
        Trip(
            id=None,
            route_id=route.id,
            trip_id="t1",
            service_id="WEEKDAY",
            schedule_version_id=version.id,
        )
    )
    trip_repository.save(
        Trip(
            id=None,
            route_id=route.id,
            trip_id="t2",
            service_id="WEEKDAY",
            schedule_version_id=version.id,
        )
    )
    trip_repository.save(
        Trip(
            id=None,
            route_id=route.id,
            trip_id="t3",
            service_id="SATURDAY",
            schedule_version_id=version.id,
        )
    )

    repo = SqlAlchemyAnalyticsRepository(session)
    result = repo.count_trips_by_day(route.id)

    assert result == {"WEEKDAY": 2, "SATURDAY": 1}


def test_average_headway_returns_none_for_single_trip(
    session: Session,
    agency: Agency,
    route_repository: SqlAlchemyRouteRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    trip_repository: SqlAlchemyTripRepository,
    stop_repository: SqlAlchemyStopRepository,
    stoptime_repository: SqlAlchemyStopTimeRepository,
) -> None:
    assert agency.id is not None

    route = route_repository.save(
        Route(
            id=None,
            agency_id=agency.id,
            route_id="1003",
            short_name="1003",
            long_name="Station",
            route_type=3,
        )
    )
    assert route.id is not None

    version = schedule_version_repository.save(
        ScheduleVersion(
            id=None,
            checksum="a" * 64,
            imported_at=datetime.now(UTC),
        )
    )
    assert version.id is not None

    stop = stop_repository.save(
        Stop(
            id=None,
            stop_id="s1",
            name="Station",
            latitude=50.0,
            longitude=36.0,
        )
    )
    assert stop.id is not None

    trip = trip_repository.save(
        Trip(
            id=None,
            route_id=route.id,
            trip_id="t1",
            service_id="WEEKDAY",
            schedule_version_id=version.id,
        )
    )
    assert trip.id is not None

    stoptime_repository.save(
        StopTime(
            id=None,
            trip_id=trip.id,
            stop_id=stop.id,
            arrival_time="08:00:00",
            departure_time="08:00:00",
            stop_sequence=1,
        )
    )

    repo = SqlAlchemyAnalyticsRepository(session)
    assert repo.average_headway_minutes(route.id) is None


def test_average_headway_returns_average(
    session: Session,
    agency: Agency,
    route_repository: SqlAlchemyRouteRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    trip_repository: SqlAlchemyTripRepository,
    stop_repository: SqlAlchemyStopRepository,
    stoptime_repository: SqlAlchemyStopTimeRepository,
) -> None:
    assert agency.id is not None

    route = route_repository.save(
        Route(
            id=None,
            agency_id=agency.id,
            route_id="1004",
            short_name="1004",
            long_name="Station",
            route_type=3,
        )
    )
    assert route.id is not None

    version = schedule_version_repository.save(
        ScheduleVersion(
            id=None,
            checksum="a" * 64,
            imported_at=datetime.now(UTC),
        )
    )
    assert version.id is not None

    stop = stop_repository.save(
        Stop(
            id=None,
            stop_id="s1",
            name="Station",
            latitude=50.0,
            longitude=36.0,
        )
    )
    assert stop.id is not None

    for i, time_str in enumerate(["08:00:00", "08:10:00", "08:20:00"]):
        trip = trip_repository.save(
            Trip(
                id=None,
                route_id=route.id,
                trip_id=f"t{i}",
                service_id="WEEKDAY",
                schedule_version_id=version.id,
            )
        )
        assert trip.id is not None
        stoptime_repository.save(
            StopTime(
                id=None,
                trip_id=trip.id,
                stop_id=stop.id,
                arrival_time=time_str,
                departure_time=time_str,
                stop_sequence=1,
            )
        )

    repo = SqlAlchemyAnalyticsRepository(session)
    result = repo.average_headway_minutes(route.id)

    assert result == 10.0


def test_top_stops_returns_ranking(
    session: Session,
    agency: Agency,
    route_repository: SqlAlchemyRouteRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    trip_repository: SqlAlchemyTripRepository,
    stop_repository: SqlAlchemyStopRepository,
    stoptime_repository: SqlAlchemyStopTimeRepository,
) -> None:
    assert agency.id is not None

    route_1 = route_repository.save(
        Route(
            id=None,
            agency_id=agency.id,
            route_id="1005",
            short_name="1005",
            long_name="Station",
            route_type=3,
        )
    )
    route_2 = route_repository.save(
        Route(
            id=None,
            agency_id=agency.id,
            route_id="1006",
            short_name="1006",
            long_name="Center",
            route_type=3,
        )
    )
    assert route_1.id is not None
    assert route_2.id is not None

    version = schedule_version_repository.save(
        ScheduleVersion(
            id=None,
            checksum="a" * 64,
            imported_at=datetime.now(UTC),
        )
    )
    assert version.id is not None

    stop_1 = stop_repository.save(
        Stop(
            id=None,
            stop_id="s1",
            name="Station",
            latitude=50.0,
            longitude=36.0,
        )
    )
    stop_2 = stop_repository.save(
        Stop(
            id=None,
            stop_id="s2",
            name="Center",
            latitude=50.0,
            longitude=36.0,
        )
    )
    assert stop_1.id is not None
    assert stop_2.id is not None

    trip_1 = trip_repository.save(
        Trip(
            id=None,
            route_id=route_1.id,
            trip_id="t1",
            service_id="WEEKDAY",
            schedule_version_id=version.id,
        )
    )
    assert trip_1.id is not None
    stoptime_repository.save(
        StopTime(
            id=None,
            trip_id=trip_1.id,
            stop_id=stop_1.id,
            arrival_time="08:00:00",
            departure_time="08:00:00",
            stop_sequence=1,
        )
    )
    stoptime_repository.save(
        StopTime(
            id=None,
            trip_id=trip_1.id,
            stop_id=stop_2.id,
            arrival_time="08:10:00",
            departure_time="08:10:00",
            stop_sequence=2,
        )
    )

    trip_2 = trip_repository.save(
        Trip(
            id=None,
            route_id=route_2.id,
            trip_id="t2",
            service_id="WEEKDAY",
            schedule_version_id=version.id,
        )
    )
    assert trip_2.id is not None
    stoptime_repository.save(
        StopTime(
            id=None,
            trip_id=trip_2.id,
            stop_id=stop_1.id,
            arrival_time="09:00:00",
            departure_time="09:00:00",
            stop_sequence=1,
        )
    )

    repo = SqlAlchemyAnalyticsRepository(session)
    result = repo.top_stops()

    assert result == [(stop_1.id, 2), (stop_2.id, 1)]
