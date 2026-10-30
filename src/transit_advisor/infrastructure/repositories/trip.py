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
            trip_id=trip.trip_id, route_id=trip.route_id, headsign=trip.headsign
        )

        self._session.add(trip_model)
        self._session.commit()
        self._session.refresh(trip_model)

        return Trip(
            id=trip_model.id,
            trip_id=trip_model.trip_id,
            route_id=trip_model.route_id,
            headsign=trip_model.headsign,
        )

    def find_by_trip_id(self, trip_id: str) -> Trip | None:
        statement = select(TripModel).where(
            TripModel.trip_id == trip_id,
        )

        trip_model = self._session.scalar(statement)

        if trip_model is None:
            return None

        return Trip(
            id=trip_model.id,
            trip_id=trip_model.trip_id,
            route_id=trip_model.route_id,
            headsign=trip_model.headsign,
        )
