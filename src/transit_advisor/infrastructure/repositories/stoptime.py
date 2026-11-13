from datetime import time

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from transit_advisor.domain.stoptime import StopTime
from transit_advisor.infrastructure.database.models.stoptime import StopTimeModel
from transit_advisor.infrastructure.database.models.trip import TripModel


class SqlAlchemyStopTimeRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, stop_time: StopTime) -> StopTime:
        model = self._to_model(stop_time)
        self._session.add(model)
        self._session.flush()
        return self._to_domain(model)

    def save_all(self, stop_times: list[StopTime]) -> list[StopTime]:
        """Bulk insert — один INSERT на весь батч."""
        if not stop_times:
            return []
        models = [self._to_model(st) for st in stop_times]
        self._session.add_all(models)
        self._session.flush()
        return [self._to_domain(m) for m in models]

    def find_by_trip_id(self, trip_id: int) -> list[StopTime]:
        statement = (
            select(StopTimeModel)
            .where(StopTimeModel.trip_id == trip_id)
            .order_by(StopTimeModel.stop_sequence)
        )
        return [self._to_domain(m) for m in self._session.scalars(statement)]

    def find_by_trip_ids(self, trip_ids: list[int]) -> list[StopTime]:
        if not trip_ids:
            return []
        statement = (
            select(StopTimeModel)
            .where(StopTimeModel.trip_id.in_(trip_ids))
            .order_by(StopTimeModel.trip_id, StopTimeModel.stop_sequence)
        )
        return [self._to_domain(m) for m in self._session.scalars(statement)]

    def find_by_stop_id(self, stop_id: int) -> list[StopTime]:
        statement = (
            select(StopTimeModel)
            .where(StopTimeModel.stop_id == stop_id)
            .order_by(StopTimeModel.arrival_time)
        )
        return [self._to_domain(m) for m in self._session.scalars(statement)]

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
        return [self._to_domain(m) for m in self._session.scalars(statement)]

    def find_departures(
        self,
        stop_id: int,
        from_time: time | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[StopTime]:
        statement = select(StopTimeModel).where(StopTimeModel.stop_id == stop_id)

        if from_time is not None:
            # УВАГА: лексикографічне порівняння рядків "HH:MM:SS".
            # Коректно лише для годин 00–23. Для GTFS з годинами >24 — не працює.
            from_str = from_time.strftime("%H:%M:%S")
            statement = statement.where(StopTimeModel.departure_time >= from_str)

        statement = (
            statement.order_by(StopTimeModel.departure_time).offset(offset).limit(limit)
        )
        return [self._to_domain(m) for m in self._session.scalars(statement)]

    def find_direct_journeys(
        self,
        from_stop_id: int,
        to_stop_id: int,
        schedule_version_id: int | None = None,
        from_time: time | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[tuple[StopTime, StopTime]]:
        st1 = aliased(StopTimeModel)
        st2 = aliased(StopTimeModel)

        statement = select(st1, st2).where(
            st1.trip_id == st2.trip_id,
            st1.stop_id == from_stop_id,
            st2.stop_id == to_stop_id,
            st1.stop_sequence < st2.stop_sequence,
        )

        if schedule_version_id is not None:
            statement = statement.join(TripModel, st1.trip_id == TripModel.id).where(
                TripModel.schedule_version_id == schedule_version_id
            )

        if from_time is not None:
            statement = statement.where(
                st1.departure_time >= from_time.strftime("%H:%M:%S")
            )

        statement = statement.order_by(st1.departure_time).offset(offset).limit(limit)

        results = self._session.execute(statement).all()
        return [(self._to_domain(r[0]), self._to_domain(r[1])) for r in results]

    def _to_model(self, stop_time: StopTime) -> StopTimeModel:
        return StopTimeModel(
            trip_id=stop_time.trip_id,
            stop_id=stop_time.stop_id,
            arrival_time=stop_time.arrival_time,
            departure_time=stop_time.departure_time,
            stop_sequence=stop_time.stop_sequence,
        )

    def _to_domain(self, model: StopTimeModel) -> StopTime:
        return StopTime(
            id=model.id,
            trip_id=model.trip_id,
            stop_id=model.stop_id,
            arrival_time=model.arrival_time,
            departure_time=model.departure_time,
            stop_sequence=model.stop_sequence,
        )
