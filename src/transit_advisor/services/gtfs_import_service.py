from transit_advisor.domain.repositories.agency import AgencyRepository
from transit_advisor.domain.repositories.route import RouteRepository
from transit_advisor.domain.repositories.stop import StopRepository
from transit_advisor.domain.repositories.stoptime import StopTimeRepository
from transit_advisor.domain.repositories.trip import TripRepository
from transit_advisor.infrastructure.gtfs.mappers.agency import to_agency
from transit_advisor.infrastructure.gtfs.mappers.route import to_route
from transit_advisor.infrastructure.gtfs.mappers.stop import to_stop
from transit_advisor.infrastructure.gtfs.mappers.stoptime import to_stoptime
from transit_advisor.infrastructure.gtfs.mappers.trip import to_trip


class GtfsImportService:
    def __init__(
        self,
        agency_repository: AgencyRepository,
        route_repository: RouteRepository,
        stop_repository: StopRepository,
        trip_repository: TripRepository,
        stoptime_repository: StopTimeRepository,
    ) -> None:
        self._agency_repository = agency_repository
        self._route_repository = route_repository
        self._stop_repository = stop_repository
        self._trip_repository = trip_repository
        self._stoptime_repository = stoptime_repository

    def import_agencies(
        self,
        rows: list[dict[str, str]],
    ) -> int:
        imported = 0

        for row in rows:
            agency = to_agency(row)

            if agency is None:
                continue

            self._agency_repository.save(agency)
            imported += 1

        return imported

    def import_routes(
        self,
        rows: list[dict[str, str]],
    ) -> int:
        imported = 0

        for row in rows:
            gtfs_agency_id = row.get(
                "agency_id",
                "",
            )

            agency = self._agency_repository.find_by_agency_id(
                gtfs_agency_id,
            )

            if agency is None:
                continue

            if agency.id is None:
                continue

            route = to_route(
                row=row,
                agency_id=agency.id,
            )

            if route is None:
                continue

            self._route_repository.save(
                route,
            )

            imported += 1

        return imported

    def import_stops(
        self,
        rows: list[dict[str, str]],
    ) -> int:
        imported = 0

        for row in rows:
            stop = to_stop(row)

            if stop is None:
                continue

            self._stop_repository.save(stop)
            imported += 1

        return imported

    def import_trips(
        self,
        rows: list[dict[str, str]],
    ) -> int:
        imported = 0

        for row in rows:
            gtfs_route_id = row.get("route_id", "")

            route = self._route_repository.find_by_route_id(gtfs_route_id)

            if route is None or route.id is None:
                continue

            trip = to_trip(
                row=row,
                route_id=route.id,
            )

            if trip is None:
                continue

            self._trip_repository.save(trip)
            imported += 1

        return imported

    def import_stoptimes(
        self,
        rows: list[dict[str, str]],
    ) -> int:
        imported = 0

        for row in rows:
            trip = self._trip_repository.find_by_trip_id(
                row.get("trip_id", ""),
            )

            stop = self._stop_repository.find_by_stop_id(
                row.get("stop_id", ""),
            )

            if trip is None or stop is None:
                continue

            if trip.id is None or stop.id is None:
                continue

            stop_time = to_stoptime(
                row=row,
                trip_id=trip.id,
                stop_id=stop.id,
            )

            if stop_time is None:
                continue

            self._stoptime_repository.save(
                stop_time,
            )

            imported += 1

        return imported
