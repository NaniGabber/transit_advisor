from transit_advisor.domain.repositories.stoptime import StopTimeRepository


class JourneyService:
    def __init__(
        self,
        stoptime_repository: StopTimeRepository,
    ) -> None:
        self._stoptime_repository = stoptime_repository

    def find_direct_journeys(
        self,
        from_stop_id: int,
        to_stop_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict[str, object]]:
        journeys = self._stoptime_repository.find_direct_journeys(
            from_stop_id=from_stop_id,
            to_stop_id=to_stop_id,
            limit=limit,
            offset=offset,
        )

        result = []
        for departure, arrival in journeys:
            result.append(
                {
                    "trip_id": departure.trip_id,
                    "from_stop_id": departure.stop_id,
                    "to_stop_id": arrival.stop_id,
                    "departure_time": departure.departure_time,
                    "arrival_time": arrival.arrival_time,
                    "stop_sequence_start": departure.stop_sequence,
                    "stop_sequence_end": arrival.stop_sequence,
                }
            )
        return result
