from transit_advisor.domain.stoptime import StopTime
from transit_advisor.infrastructure.gtfs.parsing import normalize, parse_int


def to_stoptime(
    row: dict[str, str],
    trip_id: int,
    stop_id: int,
) -> StopTime | None:
    stop_sequence = parse_int(
        row.get("stop_sequence", ""),
    )

    if stop_sequence is None:
        return None

    try:
        return StopTime(
            id=None,
            trip_id=trip_id,
            stop_id=stop_id,
            arrival_time=normalize(
                row.get("arrival_time", ""),
            ),
            departure_time=normalize(
                row.get("departure_time", ""),
            ),
            stop_sequence=stop_sequence,
        )
    except ValueError:
        return None
