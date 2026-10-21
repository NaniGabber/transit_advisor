from transit_advisor.domain.agency import Agency
from transit_advisor.domain.route import Route
from transit_advisor.domain.stop import Stop
from transit_advisor.domain.trip import Trip
from transit_advisor.services.gtfs_import_service import GtfsImportService


class FakeAgencyRepository:
    def __init__(self) -> None:
        self.saved: list[Agency] = []

    def save(self, agency: Agency) -> Agency:
        if agency.id is None:
            agency.id = len(self.saved) + 1
        self.saved.append(agency)
        return agency

    def find_by_agency_id(self, agency_id: str) -> Agency | None:
        for agency in self.saved:
            if agency.agency_id == agency_id:
                return agency
        return None


class FakeRouteRepository:
    def __init__(self) -> None:
        self.saved: list[Route] = []

    def save(self, route: Route) -> Route:
        if route.id is None:
            route.id = len(self.saved) + 1
        self.saved.append(route)
        return route

    def find_by_route_id(self, route_id: str) -> Route | None:
        for route in self.saved:
            if route.route_id == route_id:
                return route
        return None


class FakeStopRepository:
    def __init__(self) -> None:
        self.saved: list[Stop] = []

    def save(self, stop: Stop) -> Stop:
        if stop.id is None:
            stop.id = len(self.saved) + 1
        self.saved.append(stop)
        return stop

    def find_by_stop_id(self, stop_id: str) -> Stop | None:
        for stop in self.saved:
            if stop.stop_id == stop_id:
                return stop
        return None


class FakeTripRepository:
    def __init__(self) -> None:
        self.saved: list[Trip] = []

    def save(self, trip: Trip) -> Trip:
        if trip.id is None:
            trip.id = len(self.saved) + 1
        self.saved.append(trip)
        return trip

    # ВИПРАВЛЕНО: метод названо правильно, і шукає він по trip_id
    def find_by_trip_id(self, trip_id: str) -> Trip | None:
        for trip in self.saved:
            if trip.trip_id == trip_id:
                return trip
        return None


class FakeContainer:
    def __init__(self) -> None:
        self.agency_repository = FakeAgencyRepository()
        self.route_repository = FakeRouteRepository()
        self.stop_repository = FakeStopRepository()
        self.trip_repository = FakeTripRepository()

        self.service = GtfsImportService(
            agency_repository=self.agency_repository,
            route_repository=self.route_repository,
            stop_repository=self.stop_repository,
            trip_repository=self.trip_repository,
        )


def get_service() -> FakeContainer:
    """Повертає контейнер із сервісом та репозиторіями."""
    return FakeContainer()
