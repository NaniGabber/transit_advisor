from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from transit_advisor.api.dependencies import (
    get_route_repository,
    get_schedule_update_service,
)
from transit_advisor.api.schemas import RouteDiffResponse, RouteResponse
from transit_advisor.infrastructure.repositories.route import (
    SqlAlchemyRouteRepository,
)
from transit_advisor.services.schedule_update_service import ScheduleUpdateService

router = APIRouter(prefix="/routes", tags=["routes"])


@router.get(
    "/{route_id}/diff",
    response_model=RouteDiffResponse,
)
def get_route_diff(
    route_id: int,
    from_version: int = Query(..., alias="from_version"),
    to_version: int = Query(..., alias="to_version"),
    service: ScheduleUpdateService = Depends(get_schedule_update_service),
) -> RouteDiffResponse:
    try:
        diff = service.compare_route_versions(
            route_id=route_id,
            from_version_id=from_version,
            to_version_id=to_version,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return RouteDiffResponse(
        from_version=from_version,
        to_version=to_version,
        added_routes=diff.added_routes,
        removed_routes=diff.removed_routes,
        changed_stop_times=diff.changed_stop_times,
    )


router = APIRouter(prefix="/routes", tags=["routes"])


@router.get(
    "",
    response_model=list[RouteResponse],
)
def search_routes(
    repository: Annotated[
        SqlAlchemyRouteRepository,
        Depends(get_route_repository),
    ],
    q: Annotated[
        str | None, Query(description="Search by route number or name")
    ] = None,
    stop: Annotated[int | None, Query(description="Filter by stop ID")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
) -> list[RouteResponse]:
    offset = (page - 1) * page_size
    routes = repository.search(
        query=q,
        stop_id=stop,
        offset=offset,
        limit=page_size,
    )

    return [RouteResponse.model_validate(route) for route in routes]
