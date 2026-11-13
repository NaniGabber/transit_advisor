from collections.abc import Iterator
from pathlib import Path

from transit_advisor.domain.agency import Agency
from transit_advisor.domain.repositories.agency import AgencyRepository
from transit_advisor.domain.repositories.route import RouteRepository
from transit_advisor.domain.repositories.stop import StopRepository
from transit_advisor.domain.repositories.stoptime import StopTimeRepository
from transit_advisor.domain.repositories.trip import TripRepository
from transit_advisor.domain.route import Route
from transit_advisor.domain.stop import Stop
from transit_advisor.domain.stoptime import StopTime
from transit_advisor.domain.trip import Trip
from transit_advisor.domain.upload_result import ImportStats
from transit_advisor.infrastructure.archive.gtfs_archive_reader import GtfsArchiveReader
from transit_advisor.infrastructure.gtfs.mappers.agency import to_agency
from transit_advisor.infrastructure.gtfs.mappers.route import to_route
from transit_advisor.infrastructure.gtfs.mappers.stop import to_stop
from transit_advisor.infrastructure.gtfs.mappers.stoptime import to_stoptime
from transit_advisor.infrastructure.gtfs.mappers.trip import to_trip

BATCH_SIZE = 1000


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

    def import_all(
        self,
        archive_path: Path,
        reader: GtfsArchiveReader,
        schedule_version_id: int,
    ) -> dict[str, ImportStats]:
        stats: dict[str, ImportStats] = {}

        if reader.exists(archive_path, "agency.txt"):
            stats["agencies"] = self.import_agencies(
                reader.read_csv(archive_path, "agency.txt")
            )

        if reader.exists(archive_path, "routes.txt"):
            stats["routes"] = self.import_routes(
                reader.read_csv(archive_path, "routes.txt")
            )

        if reader.exists(archive_path, "stops.txt"):
            stats["stops"] = self.import_stops(
                reader.read_csv(archive_path, "stops.txt")
            )

        if reader.exists(archive_path, "trips.txt"):
            stats["trips"] = self.import_trips(
                reader.read_csv(archive_path, "trips.txt"),
                schedule_version_id,
            )

        if reader.exists(archive_path, "stop_times.txt"):
            stats["stop_times"] = self.import_stoptimes(
                reader.read_csv(archive_path, "stop_times.txt")
            )

        return stats

    def import_agencies(
        self,
        rows: Iterator[dict[str, str]],
    ) -> ImportStats:
        imported = 0
        rejected = 0
        batch: list[Agency] = []

        for row in rows:
            agency = to_agency(row)
            if agency is None:
                rejected += 1
                continue

            batch.append(agency)
            if len(batch) >= BATCH_SIZE:
                self._agency_repository.save_all(batch)
                imported += len(batch)
                batch.clear()

        if batch:
            self._agency_repository.save_all(batch)
            imported += len(batch)

        return ImportStats(imported=imported, rejected=rejected)

    def import_routes(
        self,
        rows: Iterator[dict[str, str]],
    ) -> ImportStats:
        imported = 0
        rejected = 0
        batch: list[Route] = []
        agency_cache: dict[str, int] = {}

        for row in rows:
            gtfs_agency_id = row.get("agency_id", "")

            agency_id = agency_cache.get(gtfs_agency_id)
            if agency_id is None:
                agency = self._agency_repository.find_by_agency_id(gtfs_agency_id)
                if agency is None or agency.id is None:
                    rejected += 1
                    continue
                agency_id = agency.id
                agency_cache[gtfs_agency_id] = agency_id

            route = to_route(row=row, agency_id=agency_id)
            if route is None:
                rejected += 1
                continue

            batch.append(route)
            if len(batch) >= BATCH_SIZE:
                self._route_repository.save_all(batch)
                imported += len(batch)
                batch.clear()

        if batch:
            self._route_repository.save_all(batch)
            imported += len(batch)

        return ImportStats(imported=imported, rejected=rejected)

    def import_stops(
        self,
        rows: Iterator[dict[str, str]],
    ) -> ImportStats:
        imported = 0
        rejected = 0
        batch: list[Stop] = []

        for row in rows:
            stop = to_stop(row)
            if stop is None:
                rejected += 1
                continue

            batch.append(stop)
            if len(batch) >= BATCH_SIZE:
                self._stop_repository.save_all(batch)
                imported += len(batch)
                batch.clear()

        if batch:
            self._stop_repository.save_all(batch)
            imported += len(batch)

        return ImportStats(imported=imported, rejected=rejected)

    def import_trips(
        self,
        rows: Iterator[dict[str, str]],
        schedule_version_id: int,
    ) -> ImportStats:
        imported = 0
        rejected = 0
        batch: list[Trip] = []
        route_cache: dict[str, int] = {}

        for row in rows:
            gtfs_route_id = row.get("route_id", "")

            route_id = route_cache.get(gtfs_route_id)
            if route_id is None:
                route = self._route_repository.find_by_route_id(gtfs_route_id)
                if route is None or route.id is None:
                    rejected += 1
                    continue
                route_id = route.id
                route_cache[gtfs_route_id] = route_id

            trip = to_trip(
                row=row,
                route_id=route_id,
                schedule_version_id=schedule_version_id,
            )
            if trip is None:
                rejected += 1
                continue

            batch.append(trip)
            if len(batch) >= BATCH_SIZE:
                self._trip_repository.save_all(batch)
                imported += len(batch)
                batch.clear()

        if batch:
            self._trip_repository.save_all(batch)
            imported += len(batch)

        return ImportStats(imported=imported, rejected=rejected)

    def import_stoptimes(
        self,
        rows: Iterator[dict[str, str]],
    ) -> ImportStats:
        imported = 0
        rejected = 0
        batch: list[StopTime] = []

        trip_cache: dict[str, int] = {}
        stop_cache: dict[str, int] = {}

        for row in rows:
            gtfs_trip_id = row.get("trip_id", "")
            gtfs_stop_id = row.get("stop_id", "")

            trip_id = trip_cache.get(gtfs_trip_id)
            if trip_id is None:
                trip = self._trip_repository.find_by_trip_id(gtfs_trip_id)
                if trip is None or trip.id is None:
                    rejected += 1
                    continue
                trip_id = trip.id
                trip_cache[gtfs_trip_id] = trip_id

            stop_id = stop_cache.get(gtfs_stop_id)
            if stop_id is None:
                stop = self._stop_repository.find_by_stop_id(gtfs_stop_id)
                if stop is None or stop.id is None:
                    rejected += 1
                    continue
                stop_id = stop.id
                stop_cache[gtfs_stop_id] = stop_id

            stop_time = to_stoptime(
                row=row,
                trip_id=trip_id,
                stop_id=stop_id,
            )
            if stop_time is None:
                rejected += 1
                continue

            batch.append(stop_time)
            if len(batch) >= BATCH_SIZE:
                self._stoptime_repository.save_all(batch)
                imported += len(batch)
                batch.clear()

        if batch:
            self._stoptime_repository.save_all(batch)
            imported += len(batch)

        return ImportStats(imported=imported, rejected=rejected)
