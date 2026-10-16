from transit_advisor.domain.stop import Stop
from transit_advisor.infrastructure.gtfs.parsing import normalize, parse_float


def to_stop(row: dict[str, str]) -> Stop | None:
    latitude = parse_float(
        row.get("stop_lat", ""),
    )

    longitude = parse_float(
        row.get("stop_lon", ""),
    )

    if latitude is None or longitude is None:
        return None

    try:
        return Stop(
            id=None,
            stop_id=normalize(
                row.get("stop_id", ""),
            ),
            name=normalize(
                row.get("stop_name", ""),
            ),
            latitude=latitude,
            longitude=longitude,
            code=row.get("stop_code"),
            description=row.get("stop_desc"),
        )
    except ValueError:
        return None
