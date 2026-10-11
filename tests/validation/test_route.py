import pytest

from transit_advisor.domain.route import Route


@pytest.mark.parametrize(
    "agency_id, route_id, short_name, route_type",
    [
        (0, "11", "11", 3),
        (-1, "11", "11", 3),
        (1, "", "11", 3),
        (1, "11", "", 3),
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
