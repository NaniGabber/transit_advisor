from transit_advisor.infrastructure.gtfs.mappers.route import (
    to_route,
)


def test_to_route_returns_route_for_valid_row() -> None:
    row = {
        "route_id": "11",
        "route_short_name": "11",
        "route_long_name": "Railway Station - Center",
        "route_type": "3",
    }

    route = to_route(
        row=row,
        agency_id=1,
    )

    assert route is not None
    assert route.route_id == "11"
    assert route.short_name == "11"
    assert route.route_type == 3


def test_to_route_returns_none_for_invalid_route_type() -> None:
    row = {
        "route_id": "11",
        "route_short_name": "11",
        "route_long_name": "Railway Station - Center",
        "route_type": "abc",
    }

    assert (
        to_route(
            row=row,
            agency_id=1,
        )
        is None
    )
