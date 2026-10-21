from transit_advisor.domain.agency import Agency
from transit_advisor.domain.route import Route


class FakeAgencyRepository:
    def __init__(self) -> None:
        self.saved: list[Agency] = []

    def save(
        self,
        agency: Agency,
    ) -> Agency:
        self.saved.append(agency)
        return agency

    def find_by_agency_id(
        self,
        agency_id: str,
    ) -> Agency | None:
        for agency in self.saved:
            if agency.agency_id == agency_id:
                return agency

        return None


class FakeRouteRepository:
    def __init__(self) -> None:
        self.saved: list[Route] = []

    def save(
        self,
        route: Route,
    ) -> Route:
        self.saved.append(route)
        return route

    def find_by_route_id(
        self,
        route_id: str,
    ) -> Route | None:
        for route in self.saved:
            if route.route_id == route_id:
                return route

        return None
