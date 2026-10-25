from transit_advisor.domain.agency import Agency
from transit_advisor.domain.route import Route
from transit_advisor.domain.trip import Trip
from transit_advisor.infrastructure.repositories.agency import (
    SqlAlchemyAgencyRepository,
)
from transit_advisor.infrastructure.repositories.route import (
    SqlAlchemyRouteRepository,
)
from transit_advisor.infrastructure.repositories.trip import (
    SqlAlchemyTripRepository,
)


def test_save_trip(
    agency_repository: SqlAlchemyAgencyRepository,
    route_repository: SqlAlchemyRouteRepository,
    trip_repository: SqlAlchemyTripRepository,
) -> None:
    agency = agency_repository.save(
        Agency(
            id=None,
            agency_id="metro",
            name="Kharkiv Metro",
            timezone="Europe/Kyiv",
        )
    )

    assert agency.id is not None

    route = route_repository.save(
        Route(
            id=None,
            agency_id=agency.id,
            route_id="11",
            short_name="11",
            long_name="Railway Station",
            route_type=3,
        )
    )

    assert route.id is not None

    trip = Trip(
        id=None,
        route_id=route.id,
        trip_id="trip_1",
        headsign="City Center",
    )

    saved = trip_repository.save(trip)

    assert saved.id is not None
    assert saved.trip_id == "trip_1"


def test_find_by_trip_id(
    agency_repository: SqlAlchemyAgencyRepository,
    route_repository: SqlAlchemyRouteRepository,
    trip_repository: SqlAlchemyTripRepository,
) -> None:
    agency = agency_repository.save(
        Agency(
            id=None,
            agency_id="metro",
            name="Kharkiv Metro",
            timezone="Europe/Kyiv",
        )
    )
    if agency.id is None:
        assert agency.id is not None

    route = route_repository.save(
        Route(
            id=None,
            agency_id=agency.id,
            route_id="11",
            short_name="11",
            long_name="Railway Station",
            route_type=3,
        )
    )
    if route.id is None:
        assert route.id is not None

    trip_repository.save(
        Trip(
            id=None,
            route_id=route.id,
            trip_id="trip_1",
            headsign="City Center",
        )
    )

    found = trip_repository.find_by_trip_id(
        "trip_1",
    )

    assert found is not None
    assert found.trip_id == "trip_1"
    assert found.headsign == "City Center"


def test_find_by_trip_id_returns_none_for_missing_trip(
    trip_repository: SqlAlchemyTripRepository,
) -> None:
    found = trip_repository.find_by_trip_id(
        "missing",
    )

    assert found is None


def test_saved_trip_can_be_loaded(
    agency_repository: SqlAlchemyAgencyRepository,
    route_repository: SqlAlchemyRouteRepository,
    trip_repository: SqlAlchemyTripRepository,
) -> None:
    agency = agency_repository.save(
        Agency(
            id=None,
            agency_id="metro",
            name="Kharkiv Metro",
            timezone="Europe/Kyiv",
        )
    )

    if agency.id is None:
        assert agency.id is not None

    route = route_repository.save(
        Route(
            id=None,
            agency_id=agency.id,
            route_id="11",
            short_name="11",
            long_name="Railway Station",
            route_type=3,
        )
    )

    if route.id is None:
        assert route.id is not None

    saved = trip_repository.save(
        Trip(
            id=None,
            route_id=route.id,
            trip_id="trip_1",
            headsign="City Center",
        )
    )

    loaded = trip_repository.find_by_trip_id(
        saved.trip_id,
    )

    assert loaded is not None
    assert loaded.trip_id == saved.trip_id
    assert loaded.route_id == saved.route_id
