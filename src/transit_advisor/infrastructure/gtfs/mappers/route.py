from transit_advisor.domain.route import Route


def normalize(value: str) -> str:
    return " ".join(value.split())


def parse_route_type(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def to_route(
    row: dict[str, str],
    agency_id: int,
) -> Route | None:
    route_type = parse_route_type(
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
