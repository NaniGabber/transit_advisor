from sqlalchemy import select
from sqlalchemy.orm import Session

from transit_advisor.domain.stop import Stop
from transit_advisor.infrastructure.database.models.stop import StopModel


class SqlAlchemyStopRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def save(self, stop: Stop) -> Stop:
        model = self._to_model(stop)
        self._session.add(model)
        self._session.flush()
        return self._to_domain(model)

    def save_all(self, stops: list[Stop]) -> list[Stop]:
        """Bulk insert — один INSERT на весь батч."""
        if not stops:
            return []
        models = [self._to_model(s) for s in stops]
        self._session.add_all(models)
        self._session.flush()
        return [self._to_domain(m) for m in models]

    def find_by_stop_id(self, stop_id: str) -> Stop | None:
        statement = select(StopModel).where(
            StopModel.stop_id == stop_id,
        )
        model = self._session.scalar(statement)
        if model is None:
            return None
        return self._to_domain(model)

    def find_by_stop_ids(self, stop_ids: list[str]) -> dict[str, Stop]:
        """Bulk lookup. Один SELECT, повертає dict для O(1) доступу."""
        if not stop_ids:
            return {}
        statement = select(StopModel).where(
            StopModel.stop_id.in_(stop_ids),
        )
        return {m.stop_id: self._to_domain(m) for m in self._session.scalars(statement)}

    def _to_model(self, stop: Stop) -> StopModel:
        return StopModel(
            stop_id=stop.stop_id,
            name=stop.name,
            latitude=stop.latitude,
            longitude=stop.longitude,
            code=stop.code,
            description=stop.description,
        )

    def _to_domain(self, model: StopModel) -> Stop:
        return Stop(
            id=model.id,
            stop_id=model.stop_id,
            name=model.name,
            latitude=model.latitude,
            longitude=model.longitude,
            code=model.code,
            description=model.description,
        )
