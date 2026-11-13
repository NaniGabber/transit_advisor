from sqlalchemy import select
from sqlalchemy.orm import Session

from transit_advisor.domain.trip import Trip
from transit_advisor.infrastructure.database.models.trip import TripModel


class SqlAlchemyTripRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def save(self, trip: Trip) -> Trip:
        trip_model = TripModel(
            trip_id=trip.trip_id,
            route_id=trip.route_id,
            headsign=trip.headsign,
            schedule_version_id=trip.schedule_version_id,
            service_id=trip.service_id,
        )

        self._session.add(trip_model)
        self._session.flush()

        return self._to_domain(trip_model)

    def find_by_trip_id(self, trip_id: str) -> Trip | None:
        statement = select(TripModel).where(
            TripModel.trip_id == trip_id,
        )

        trip_model = self._session.scalar(statement)

        if trip_model is None:
            return None

        return self._to_domain(trip_model)

    def find_by_schedule_version_id(
        self,
        schedule_version_id: int,
    ) -> list[Trip]:
        statement = select(TripModel).where(
            TripModel.schedule_version_id == schedule_version_id
        )
        return [self._to_domain(m) for m in self._session.scalars(statement).all()]

    def _to_domain(self, model: TripModel) -> Trip:
        return Trip(
            id=model.id,
            trip_id=model.trip_id,
            route_id=model.route_id,
            headsign=model.headsign,
            schedule_version_id=model.schedule_version_id,
            service_id=model.service_id,
        )
