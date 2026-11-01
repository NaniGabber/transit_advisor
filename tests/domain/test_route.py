import pytest

from transit_advisor.domain.route import Route


@pytest.mark.parametrize(
    "agency_id, route_id, short_name, route_type",
    [
        (0, "11", "11", 3),
        (-1, "11", "11", 3),
        (1, "", "11", 3),
        (1, " ", "11", 3),
        (1, "11", "", 3),
        (1, "11", " ", 3),
        (1, "11", "11", -1),
    ],
)
def test_invalid_route_rejected(
    agency_id: int,
    route_id: str,
    short_name: str,
    route_type: int,
) -> None:
    with pytest.raises(ValueError):
        Route(
            id=None,
            agency_id=agency_id,
            route_id=route_id,
            short_name=short_name,
            long_name="Route",
            route_type=route_type,
        )


def test_create_valid_route() -> None:
    route = Route(
        id=None,
        agency_id=1,
        route_id="11",
        short_name="11",
        long_name="Railway Station",
        route_type=3,
    )

    assert route.route_id == "11"


def test_display_name() -> None:
    route = Route(
        id=None,
        agency_id=1,
        route_id="11",
        short_name="11",
        long_name="Railway Station",
        route_type=3,
    )

    assert route.display_name == "11 Railway Station"


def test_is_bus() -> None:
    route = Route(
        id=None,
        agency_id=1,
        route_id="11",
        short_name="11",
        long_name="Railway Station",
        route_type=3,
    )

    assert route.is_bus


def test_is_tram() -> None:
    route = Route(
        id=None,
        agency_id=1,
        route_id="1",
        short_name="1",
        long_name="Central",
        route_type=0,
    )

    assert route.is_tram


def test_is_subway() -> None:
    route = Route(
        id=None,
        agency_id=1,
        route_id="M1",
        short_name="M1",
        long_name="Metro",
        route_type=1,
    )

    assert route.is_subway
