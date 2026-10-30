from sqlalchemy import select
from sqlalchemy.orm import Session

from transit_advisor.domain.stop import Stop
from transit_advisor.infrastructure.database.models.stop import (
    StopModel,
)


class SqlAlchemyStopRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def save(
        self,
        stop: Stop,
    ) -> Stop:
        stop_model = StopModel(
            stop_id=stop.stop_id,
            name=stop.name,
            latitude=stop.latitude,
            longitude=stop.longitude,
            code=stop.code,
            description=stop.description,
        )

        self._session.add(stop_model)
        self._session.commit()
        self._session.refresh(stop_model)

        return Stop(
            id=stop_model.id,
            stop_id=stop_model.stop_id,
            name=stop_model.name,
            latitude=stop_model.latitude,
            longitude=stop_model.longitude,
            code=stop_model.code,
            description=stop_model.description,
        )

    def find_by_stop_id(
        self,
        stop_id: str,
    ) -> Stop | None:
        statement = select(StopModel).where(
            StopModel.stop_id == stop_id,
        )

        stop_model = self._session.scalar(statement)

        if stop_model is None:
            return None

        return Stop(
            id=stop_model.id,
            stop_id=stop_model.stop_id,
            name=stop_model.name,
            latitude=stop_model.latitude,
            longitude=stop_model.longitude,
            code=stop_model.code,
            description=stop_model.description,
        )
