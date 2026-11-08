from sqlalchemy import select
from sqlalchemy.orm import Session

from transit_advisor.domain.route import Route
from transit_advisor.infrastructure.database.models.route import (
    RouteModel,
)
from transit_advisor.infrastructure.database.models.stoptime import StopTimeModel
from transit_advisor.infrastructure.database.models.trip import TripModel


class SqlAlchemyRouteRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def save(
        self,
        route: Route,
    ) -> Route:
        route_model = RouteModel(
            agency_id=route.agency_id,
            route_id=route.route_id,
            short_name=route.short_name,
            long_name=route.long_name,
            route_type=route.route_type,
            description=route.description,
            color=route.color,
            text_color=route.text_color,
        )

        self._session.add(route_model)
        self._session.flush()
        self._session.refresh(route_model)

        return self._to_domain(route_model)

    def find_by_route_id(
        self,
        route_id: str,
    ) -> Route | None:
        statement = select(RouteModel).where(
            RouteModel.route_id == route_id,
        )

        route_model = self._session.scalar(statement)

        if route_model is None:
            return None
        return self._to_domain(route_model)

    def find_by_id(self, route_id: int) -> Route | None:
        model = self._session.get(RouteModel, route_id)
        if model is None:
            return None
        return self._to_domain(model)

    def _to_domain(self, model: RouteModel) -> Route:
        return Route(
            id=model.id,
            agency_id=model.agency_id,
            route_id=model.route_id,
            short_name=model.short_name,
            long_name=model.long_name,
            route_type=model.route_type,
        )

    def search(
        self,
        query: str | None = None,
        stop_id: int | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Route]:
        statement = select(RouteModel)

        if query:
            pattern = f"%{query}%"
            statement = statement.where(
                (RouteModel.route_id.ilike(pattern))
                | (RouteModel.short_name.ilike(pattern))
                | (RouteModel.long_name.ilike(pattern))
            )

        if stop_id is not None:
            statement = (
                statement.join(TripModel, TripModel.route_id == RouteModel.id)
                .join(StopTimeModel, StopTimeModel.trip_id == TripModel.id)
                .where(StopTimeModel.stop_id == stop_id)
                .distinct()
            )

        statement = statement.offset(offset).limit(limit)

        models = self._session.scalars(statement).all()

        return [self._to_domain(model) for model in models]
