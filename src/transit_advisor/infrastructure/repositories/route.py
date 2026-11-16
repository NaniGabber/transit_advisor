from sqlalchemy import select
from sqlalchemy.orm import Session

from transit_advisor.domain.route import Route
from transit_advisor.infrastructure.database.models.route import RouteModel
from transit_advisor.infrastructure.database.models.stoptime import StopTimeModel
from transit_advisor.infrastructure.database.models.trip import TripModel


class SqlAlchemyRouteRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, route: Route) -> Route:
        model = self._to_model(route)
        self._session.add(model)
        self._session.flush()
        return self._to_domain(model)

    def save_all(self, routes: list[Route]) -> list[Route]:
        """Bulk insert — один INSERT на весь батч."""
        if not routes:
            return []
        models = [self._to_model(r) for r in routes]
        self._session.add_all(models)
        self._session.flush()
        return [self._to_domain(m) for m in models]

    def find_by_route_id(self, route_id: str) -> Route | None:
        statement = select(RouteModel).where(
            RouteModel.route_id == route_id,
        )
        model = self._session.scalar(statement)
        if model is None:
            return None
        return self._to_domain(model)

    def find_by_route_ids(self, route_ids: list[str]) -> dict[str, Route]:
        """Bulk lookup. Один SELECT."""
        if not route_ids:
            return {}
        statement = select(RouteModel).where(
            RouteModel.route_id.in_(route_ids),
        )
        return {
            m.route_id: self._to_domain(m) for m in self._session.scalars(statement)
        }

    def find_by_id(self, route_id: int) -> Route | None:
        model = self._session.get(RouteModel, route_id)
        if model is None:
            return None
        return self._to_domain(model)

    def search(
        self,
        query: str | None = None,
        stop_id: int | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Route]:
        statement = select(RouteModel)

        if query:
            escaped = (
                query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            )
            pattern = f"%{escaped}%"
            statement = statement.where(
                (RouteModel.route_id.ilike(pattern, escape="\\"))
                | (RouteModel.short_name.ilike(pattern, escape="\\"))
                | (RouteModel.long_name.ilike(pattern, escape="\\"))
            )

        if stop_id is not None:
            # EXISTS замість join+distinct: коректні OFFSET/LIMIT,
            # без матеріалізації тисяч stop_times на маршрут.
            statement = statement.where(
                select(TripModel.id)
                .join(StopTimeModel, StopTimeModel.trip_id == TripModel.id)
                .where(
                    TripModel.route_id == RouteModel.id,
                    StopTimeModel.stop_id == stop_id,
                )
                .exists()
            )

        statement = statement.offset(offset).limit(limit)

        return [self._to_domain(m) for m in self._session.scalars(statement)]

    def _to_model(self, route: Route) -> RouteModel:
        return RouteModel(
            agency_id=route.agency_id,
            route_id=route.route_id,
            short_name=route.short_name,
            long_name=route.long_name,
            route_type=route.route_type,
            description=route.description,
            color=route.color,
            text_color=route.text_color,
        )

    def _to_domain(self, model: RouteModel) -> Route:
        return Route(
            id=model.id,
            agency_id=model.agency_id,
            route_id=model.route_id,
            short_name=model.short_name,
            long_name=model.long_name,
            route_type=model.route_type,
        )
