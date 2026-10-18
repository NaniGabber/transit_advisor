from typing import Protocol

from transit_advisor.domain.route import Route


class RouteRepository(Protocol):
    def save(
        self,
        route: Route,
    ) -> Route: ...

    def find_by_route_id(
        self,
        route_id: str,
    ) -> Route | None: ...
