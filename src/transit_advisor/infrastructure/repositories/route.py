from sqlalchemy import select
from sqlalchemy.orm import Session

from transit_advisor.domain.route import Route
from transit_advisor.infrastructure.database.models.route import (
    RouteModel,
)


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
        self._session.commit()
        self._session.refresh(route_model)

        return Route(
            id=route_model.id,
            agency_id=route_model.agency_id,
            route_id=route_model.route_id,
            short_name=route_model.short_name,
            long_name=route_model.long_name,
            route_type=route_model.route_type,
            description=route_model.description,
            color=route_model.color,
            text_color=route_model.text_color,
        )

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

        return Route(
            id=route_model.id,
            agency_id=route_model.agency_id,
            route_id=route_model.route_id,
            short_name=route_model.short_name,
            long_name=route_model.long_name,
            route_type=route_model.route_type,
            description=route_model.description,
            color=route_model.color,
            text_color=route_model.text_color,
        )
