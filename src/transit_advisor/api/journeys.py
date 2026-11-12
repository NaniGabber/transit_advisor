from typing import Annotated

from fastapi import APIRouter, Depends, Query

from transit_advisor.api.dependencies import get_journey_service
from transit_advisor.api.schemas import JourneyResponse
from transit_advisor.services.journey_service import JourneyService

router = APIRouter(prefix="/journeys", tags=["journeys"])


@router.get(
    "",
    response_model=list[JourneyResponse],
)
def find_journeys(
    service: Annotated[JourneyService, Depends(get_journey_service)],
    from_stop: Annotated[int, Query(description="ID of the departure stop")],
    to_stop: Annotated[int, Query(description="ID of the arrival stop")],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[JourneyResponse]:
    offset = (page - 1) * page_size
    journeys = service.find_direct_journeys(
        from_stop_id=from_stop,
        to_stop_id=to_stop,
        limit=page_size,
        offset=offset,
    )
    return [
        JourneyResponse(
            trip_id=j.trip_id,
            from_stop_id=j.from_stop_id,
            to_stop_id=j.to_stop_id,
            departure_time=j.departure_time,
            arrival_time=j.arrival_time,
            stop_sequence_start=j.stop_sequence_start,
            stop_sequence_end=j.stop_sequence_end,
        )
        for j in journeys
    ]
