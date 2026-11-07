from collections.abc import Callable

import pytest

from transit_advisor.domain.agency import Agency
from transit_advisor.domain.route import Route
from transit_advisor.infrastructure.repositories.route import (
    SqlAlchemyRouteRepository,
)


@pytest.fixture
def make_route(
    route_repository: SqlAlchemyRouteRepository,
    agency: Agency,
) -> Callable[..., Route]:
    def create(
        route_id: str = "11",
        short_name: str = "11",
        long_name: str = "Railway Station",
        route_type: int = 3,
    ) -> Route:
        assert agency.id is not None
        return route_repository.save(
            Route(
                id=None,
                agency_id=agency.id,
                route_id=route_id,
                short_name=short_name,
                long_name=long_name,
                route_type=route_type,
            )
        )

    return create


def test_save_route(
    make_route: Callable[..., Route],
) -> None:
    saved = make_route()

    assert saved.id is not None


def test_find_by_route_id(
    make_route: Callable[..., Route],
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    make_route(route_id="11")

    found = route_repository.find_by_route_id("11")

    assert found is not None
    assert found.route_id == "11"
    assert found.short_name == "11"


def test_find_by_route_id_returns_none_for_missing_route(
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    found = route_repository.find_by_route_id("missing")

    assert found is None


def test_saved_route_can_be_loaded(
    make_route: Callable[..., Route],
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    saved = make_route(route_id="11")

    loaded = route_repository.find_by_route_id(saved.route_id)

    assert loaded is not None
    assert loaded.route_id == saved.route_id
    assert loaded.agency_id == saved.agency_id


def test_find_by_id_returns_route(
    make_route: Callable[..., Route],
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    saved = make_route(route_id="11")
    assert saved.id is not None

    found = route_repository.find_by_id(saved.id)

    assert found is not None
    assert found.id == saved.id
    assert found.route_id == "11"


def test_find_by_id_returns_none_for_missing_route(
    route_repository: SqlAlchemyRouteRepository,
) -> None:
    assert route_repository.find_by_id(999) is None
