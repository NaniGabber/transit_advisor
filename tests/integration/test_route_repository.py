from transit_advisor.domain.route import Route
from transit_advisor.infrastructure.repositories.route import SqlAlchemyRouteRepository


def test_save_route(route_repository: SqlAlchemyRouteRepository) -> None: ...


def test_find_by_route_id(
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    route = Route(
        id=None,
        agency_id=1,
        route_id="11",
        short_name="11",
        long_name="Railway Station",
        route_type=3,
    )

    route_repository.save(route)

    found = route_repository.find_by_route_id(
        "11",
    )

    assert found is not None
    assert found.route_id == "11"
    assert found.short_name == "11"


def test_find_by_route_id_returns_none_for_missing_route(
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    found = route_repository.find_by_route_id(
        "missing",
    )

    assert found is None


def test_saved_route_can_be_loaded(
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    route = Route(
        id=None,
        agency_id=1,
        route_id="11",
        short_name="11",
        long_name="Railway Station",
        route_type=3,
    )

    saved = route_repository.save(
        route,
    )

    loaded = route_repository.find_by_route_id(
        saved.route_id,
    )

    assert loaded is not None
    assert loaded.route_id == saved.route_id
    assert loaded.agency_id == saved.agency_id
