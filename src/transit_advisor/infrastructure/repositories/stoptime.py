from sqlalchemy import select
from sqlalchemy.orm import Session

from transit_advisor.domain.stoptime import StopTime
from transit_advisor.infrastructure.database.models.stoptime import (
    StopTimeModel,
)


class SqlAlchemyStopTimeRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def save(
        self,
        stop_time: StopTime,
    ) -> StopTime:
        stop_time_model = StopTimeModel(
            trip_id=stop_time.trip_id,
            stop_id=stop_time.stop_id,
            arrival_time=stop_time.arrival_time,
            departure_time=stop_time.departure_time,
            stop_sequence=stop_time.stop_sequence,
        )

        self._session.add(stop_time_model)
        self._session.commit()
        self._session.refresh(stop_time_model)

        return StopTime(
            id=stop_time_model.id,
            trip_id=stop_time_model.trip_id,
            stop_id=stop_time_model.stop_id,
            arrival_time=stop_time_model.arrival_time,
            departure_time=stop_time_model.departure_time,
            stop_sequence=stop_time_model.stop_sequence,
        )

    def find_by_trip_id(
        self,
        trip_id: int,
    ) -> list[StopTime]:
        statement = (
            select(StopTimeModel)
            .where(StopTimeModel.trip_id == trip_id)
            .order_by(StopTimeModel.stop_sequence)
        )

        stop_time_models = self._session.scalars(
            statement,
        ).all()

        return [
            StopTime(
                id=model.id,
                trip_id=model.trip_id,
                stop_id=model.stop_id,
                arrival_time=model.arrival_time,
                departure_time=model.departure_time,
                stop_sequence=model.stop_sequence,
            )
            for model in stop_time_models
        ]
