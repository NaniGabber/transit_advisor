from transit_advisor.domain.route import Route
from transit_advisor.infrastructure.gtfs.parsing import normalize, parse_int


def to_route(
    row: dict[str, str],
    agency_id: int,
) -> Route | None:
    route_type = parse_int(
        row.get("route_type", ""),
    )

    if route_type is None:
        return None

    try:
        return Route(
            id=None,
            agency_id=agency_id,
            route_id=normalize(
                row.get("route_id", ""),
            ),
            short_name=normalize(
                row.get("route_short_name", ""),
            ),
            long_name=normalize(
                row.get("route_long_name", ""),
            ),
            route_type=route_type,
        )
    except ValueError:
        return None
