from typing import Protocol

from transit_advisor.domain.route import Route


class RouteRepository(Protocol):
    def save(
        self,
        route: Route,
    ) -> Route: ...

    def save_all(
        self,
        routes: list[Route],
    ) -> list[Route]: ...

    def find_by_route_id(
        self,
        route_id: str,
    ) -> Route | None: ...

    def find_by_route_ids(
        self,
        route_ids: list[str],
    ) -> dict[str, Route]: ...

    def find_by_id(self, route_id: int) -> Route | None: ...

    def search(
        self,
        query: str | None = None,
        stop_id: int | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Route]: ...
