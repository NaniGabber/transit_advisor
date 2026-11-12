from typing import Annotated

from fastapi import APIRouter, Depends, Query

from transit_advisor.api.dependencies import get_analytics_service
from transit_advisor.api.schemas import (
    AverageHeadwayResponse,
    TopStopResponse,
    TopStopsResponse,
    TripsByDayResponse,
)
from transit_advisor.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/routes/{route_id}/trips-by-day",
    response_model=TripsByDayResponse,
)
def get_trips_by_day(
    route_id: int,
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> TripsByDayResponse:
    return TripsByDayResponse(
        route_id=route_id,
        trips_by_day=service.trips_by_day(route_id),
    )


@router.get(
    "/routes/{route_id}/headway",
    response_model=AverageHeadwayResponse,
)
def get_average_headway(
    route_id: int,
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> AverageHeadwayResponse:
    return AverageHeadwayResponse(
        route_id=route_id,
        average_headway_minutes=service.average_headway(route_id),
    )


@router.get(
    "/stops/top",
    response_model=TopStopsResponse,
)
def get_top_stops(
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> TopStopsResponse:
    stops = service.top_stops(limit)
    return TopStopsResponse(
        stops=[
            TopStopResponse(stop_id=stop_id, route_count=count)
            for stop_id, count in stops
        ],
    )
