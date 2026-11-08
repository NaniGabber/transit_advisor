from datetime import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from transit_advisor.domain.stoptime import StopTime
from transit_advisor.infrastructure.database.models.stoptime import (
    StopTimeModel,
)
from transit_advisor.infrastructure.database.models.trip import (
    TripModel,
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
        self._session.flush()
        self._session.refresh(stop_time_model)
        return self._to_domain(stop_time_model)

    def find_by_trip_id(
        self,
        trip_id: int,
    ) -> list[StopTime]:
        statement = (
            select(StopTimeModel)
            .where(StopTimeModel.trip_id == trip_id)
            .order_by(StopTimeModel.stop_sequence)
        )

        return [self._to_domain(m) for m in self._session.scalars(statement).all()]

    def find_by_trip_ids(self, trip_ids: list[int]) -> list[StopTime]:
        if not trip_ids:
            return []
        statement = (
            select(StopTimeModel)
            .where(StopTimeModel.trip_id.in_(trip_ids))
            .order_by(StopTimeModel.trip_id, StopTimeModel.stop_sequence)
        )
        return [self._to_domain(m) for m in self._session.scalars(statement).all()]

    def find_by_stop_id(self, stop_id: int) -> list[StopTime]:
        statement = (
            select(StopTimeModel)
            .where(StopTimeModel.stop_id == stop_id)
            .order_by(StopTimeModel.arrival_time)
        )
        return [self._to_domain(m) for m in self._session.scalars(statement).all()]

    def find_by_route_id_and_version(
        self,
        route_id: int,
        schedule_version_id: int,
    ) -> list[StopTime]:
        statement = (
            select(StopTimeModel)
            .join(TripModel, StopTimeModel.trip_id == TripModel.id)
            .where(
                TripModel.route_id == route_id,
                TripModel.schedule_version_id == schedule_version_id,
            )
            .order_by(StopTimeModel.trip_id, StopTimeModel.stop_sequence)
        )
        return [self._to_domain(m) for m in self._session.scalars(statement).all()]

    def _to_domain(self, model: StopTimeModel) -> StopTime:
        return StopTime(
            id=model.id,
            trip_id=model.trip_id,
            stop_id=model.stop_id,
            arrival_time=model.arrival_time,
            departure_time=model.departure_time,
            stop_sequence=model.stop_sequence,
        )

    def find_departures(
        self,
        stop_id: int,
        from_time: time | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[StopTime]:
        statement = select(StopTimeModel).where(StopTimeModel.stop_id == stop_id)

        if from_time is not None:
            # Порівнюємо як рядки, бо в БД час зберігається у форматі "HH:MM:SS"
            from_str = from_time.strftime("%H:%M:%S")
            statement = statement.where(StopTimeModel.departure_time >= from_str)

        statement = (
            statement.order_by(StopTimeModel.departure_time).offset(offset).limit(limit)
        )

        models = self._session.scalars(statement).all()
        return [self._to_domain(model) for model in models]
