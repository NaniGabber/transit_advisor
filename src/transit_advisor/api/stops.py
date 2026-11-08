from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from transit_advisor.api.dependencies import get_stoptime_repository
from transit_advisor.api.schemas import DepartureResponse
from transit_advisor.infrastructure.repositories.stoptime import (
    SqlAlchemyStopTimeRepository,
)

router = APIRouter(prefix="/stops", tags=["stops"])


@router.get(
    "/{stop_id}/departures",
    response_model=list[DepartureResponse],
)
def get_departures(
    stop_id: int,
    repository: Annotated[
        SqlAlchemyStopTimeRepository,
        Depends(get_stoptime_repository),
    ],
    from_time: Annotated[
        str | None,
        Query(
            alias="from",
            description="Start time in HH:MM format (e.g., 08:00). Defaults to now.",
        ),
    ] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[DepartureResponse]:
    # Парсимо час
    if from_time:
        try:
            parsed_time = datetime.strptime(from_time, "%H:%M").time()
        except ValueError as err:
            # Якщо формат неправильний, повертаємо 422
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Invalid time format. Use HH:MM.",
            ) from err
    else:
        parsed_time = datetime.now().time()

    offset = (page - 1) * page_size
    departures = repository.find_departures(
        stop_id=stop_id,
        from_time=parsed_time,
        offset=offset,
        limit=page_size,
    )

    return [DepartureResponse.model_validate(dep) for dep in departures]
