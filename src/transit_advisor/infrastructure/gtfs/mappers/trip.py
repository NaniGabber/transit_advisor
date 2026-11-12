from collections.abc import Mapping

from transit_advisor.domain.trip import Trip
from transit_advisor.infrastructure.gtfs.parsing import normalize


def to_trip(
    row: Mapping[str, str | None],
    route_id: int,
    schedule_version_id: int,
) -> Trip | None:
    try:
        return Trip(
            id=None,
            route_id=route_id,
            trip_id=normalize(
                row.get("trip_id") or "",
            ),
            service_id=normalize(row.get("service_id") or "").strip(),
            schedule_version_id=schedule_version_id,
            headsign=normalize(
                row.get("trip_headsign") or "",
            )
            or None,
        )
    except ValueError:
        return None
