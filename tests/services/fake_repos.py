from collections.abc import Iterator
from dataclasses import replace
from datetime import datetime, time
from pathlib import Path

from transit_advisor.domain.agency import Agency
from transit_advisor.domain.exceptions import AlreadySubscribedError
from transit_advisor.domain.notification import Notification
from transit_advisor.domain.route import Route
from transit_advisor.domain.scheduleversion import ScheduleVersion
from transit_advisor.domain.stop import Stop
from transit_advisor.domain.stoptime import StopTime
from transit_advisor.domain.subscription import Subscription
from transit_advisor.domain.trip import Trip
from transit_advisor.domain.upload_result import ImportStats
from transit_advisor.infrastructure.archive.gtfs_archive_reader import GtfsArchiveReader
from transit_advisor.services.checksum_service import ChecksumService
from transit_advisor.services.feed_upload_service import FeedUploadService
from transit_advisor.services.feed_validation_service import FeedValidator
from transit_advisor.services.gtfs_import_service import GtfsImportService
from transit_advisor.services.notification_service import NotificationService
from transit_advisor.services.schedule_version_service import ScheduleVersionService


class FakeAgencyRepository:
    def __init__(self) -> None:
        self.saved: list[Agency] = []

    def save(self, agency: Agency) -> Agency:
        if agency.id is None:
            agency = replace(agency, id=len(self.saved) + 1)
        self.saved.append(agency)
        return agency

    def save_all(self, agencies: list[Agency]) -> list[Agency]:
        return [self.save(a) for a in agencies]

    def find_by_agency_id(self, agency_id: str) -> Agency | None:
        for agency in self.saved:
            if agency.agency_id == agency_id:
                return agency
        return None

    def find_by_agency_ids(self, agency_ids: list[str]) -> dict[str, Agency]:
        return {a.agency_id: a for a in self.saved if a.agency_id in agency_ids}


class FakeRouteRepository:
    def __init__(self) -> None:
        self.saved: list[Route] = []

    def save(self, route: Route) -> Route:
        if route.id is None:
            route = replace(route, id=len(self.saved) + 1)
        self.saved.append(route)
        return route

    def save_all(self, routes: list[Route]) -> list[Route]:
        return [self.save(r) for r in routes]

    def find_by_route_id(self, route_id: str) -> Route | None:
        for route in self.saved:
            if route.route_id == route_id:
                return route
        return None

    def find_by_route_ids(self, route_ids: list[str]) -> dict[str, Route]:
        return {r.route_id: r for r in self.saved if r.route_id in route_ids}

    def find_by_id(self, route_id: int) -> Route | None:
        return next((r for r in self.saved if r.id == route_id), None)

    def search(
        self,
        query: str | None = None,
        stop_id: int | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Route]:
        results = self.saved

        if query:
            pattern = query.lower()
            results = [
                route
                for route in results
                if pattern in route.route_id.lower()
                or pattern in route.short_name.lower()
                or pattern in route.long_name.lower()
            ]

        if stop_id is not None:
            # У фейку немає зв'язку Trip/StopTime, тому цей фільтр
            # не може бути реалістично перевірений без додаткових даних.
            results = []

        return results[offset : offset + limit]


class FakeStopRepository:
    def __init__(self) -> None:
        self.saved: list[Stop] = []

    def save(self, stop: Stop) -> Stop:
        if stop.id is None:
            stop = replace(stop, id=len(self.saved) + 1)
        self.saved.append(stop)
        return stop

    def save_all(self, stops: list[Stop]) -> list[Stop]:
        return [self.save(s) for s in stops]

    def find_by_stop_id(self, stop_id: str) -> Stop | None:
        for stop in self.saved:
            if stop.stop_id == stop_id:
                return stop
        return None

    def find_by_stop_ids(self, stop_ids: list[str]) -> dict[str, Stop]:
        return {s.stop_id: s for s in self.saved if s.stop_id in stop_ids}


class FakeTripRepository:
    def __init__(self) -> None:
        self.saved: list[Trip] = []
        self._next_id = 1

    def save(self, trip: Trip) -> Trip:
        if trip.id is None:
            trip = replace(trip, id=self._next_id)
            self._next_id += 1
        self.saved.append(trip)
        return trip

    def save_all(self, trips: list[Trip]) -> list[Trip]:
        return [self.save(t) for t in trips]

    def find_by_trip_id(self, trip_id: str) -> Trip | None:
        return next((t for t in self.saved if t.trip_id == trip_id), None)

    def find_by_trip_ids(self, trip_ids: list[str]) -> dict[str, Trip]:
        return {t.trip_id: t for t in self.saved if t.trip_id in trip_ids}

    def find_by_schedule_version_id(
        self,
        schedule_version_id: int,
    ) -> list[Trip]:
        return [t for t in self.saved if t.schedule_version_id == schedule_version_id]

    def find_by_route_id(self, route_id: int) -> list[Trip]:
        return [t for t in self.saved if t.route_id == route_id]


class FakeStopTimeRepository:
    def __init__(self) -> None:
        self.saved: list[StopTime] = []
        self._next_id = 1

    def save(self, stop_time: StopTime) -> StopTime:
        saved = StopTime(
            id=self._next_id,
            trip_id=stop_time.trip_id,
            stop_id=stop_time.stop_id,
            arrival_time=stop_time.arrival_time,
            departure_time=stop_time.departure_time,
            stop_sequence=stop_time.stop_sequence,
        )
        self.saved.append(saved)
        self._next_id += 1
        return saved

    def save_all(self, stop_times: list[StopTime]) -> list[StopTime]:
        return [self.save(st) for st in stop_times]

    def find_by_trip_id(self, trip_id: int) -> list[StopTime]:
        return sorted(
            (st for st in self.saved if st.trip_id == trip_id),
            key=lambda st: st.stop_sequence,
        )

    def find_by_trip_ids(self, trip_ids: list[int]) -> list[StopTime]:
        return sorted(
            (st for st in self.saved if st.trip_id in trip_ids),
            key=lambda st: (st.trip_id, st.stop_sequence),
        )

    def find_by_stop_id(self, stop_id: int) -> list[StopTime]:
        return sorted(
            (st for st in self.saved if st.stop_id == stop_id),
            key=lambda st: st.arrival_time,
        )

    def find_by_route_id_and_version(
        self,
        route_id: int,
        schedule_version_id: int,
    ) -> list[StopTime]:
        raise NotImplementedError(
            "FakeStopTimeRepository does not know about trips/routes"
        )

    def find_departures(
        self,
        stop_id: int,
        from_time: time | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[StopTime]:
        results = [st for st in self.saved if st.stop_id == stop_id]

        if from_time is not None:
            from_str = from_time.strftime("%H:%M:%S")
            results = [st for st in results if st.departure_time >= from_str]

        results = sorted(results, key=lambda st: st.departure_time)

        return results[offset : offset + limit]

    def find_direct_journeys(
        self,
        from_stop_id: int,
        to_stop_id: int,
        schedule_version_id: int | None = None,
        from_time: time | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[tuple[StopTime, StopTime]]:
        """schedule_version_id приймається для сумісності з Protocol,
        але ігнорується: fake не знає про версії розкладу."""
        results: list[tuple[StopTime, StopTime]] = []

        trips: dict[int, list[StopTime]] = {}
        for stop_time in self.saved:
            trips.setdefault(stop_time.trip_id, []).append(stop_time)

        for trip_stop_times in trips.values():
            trip_stop_times.sort(key=lambda st: st.stop_sequence)

            from_st = next(
                (st for st in trip_stop_times if st.stop_id == from_stop_id),
                None,
            )
            to_st = next(
                (st for st in trip_stop_times if st.stop_id == to_stop_id),
                None,
            )

            if from_st is None or to_st is None:
                continue
            if from_st.stop_sequence >= to_st.stop_sequence:
                continue

            if from_time is not None:
                departure_time = datetime.strptime(
                    from_st.departure_time,
                    "%H:%M:%S",
                ).time()
                if departure_time < from_time:
                    continue

            results.append((from_st, to_st))

        results.sort(key=lambda pair: pair[0].departure_time)
        return results[offset : offset + limit]


class FakeScheduleVersionRepository:
    def __init__(self) -> None:
        self.saved: list[ScheduleVersion] = []

    def save(
        self,
        version: ScheduleVersion,
    ) -> ScheduleVersion:
        if version.id is None:
            version = replace(version, id=len(self.saved) + 1)
        self.saved.append(version)
        return version

    def find_by_checksum(
        self,
        checksum: str,
    ) -> ScheduleVersion | None:
        for version in self.saved:
            if version.checksum == checksum:
                return version
        return None


class FakeGtfsArchiveReader(GtfsArchiveReader):
    def __init__(self, files: set[str] | None = None) -> None:
        self._files = files or {
            "agency.txt",
            "routes.txt",
            "stops.txt",
            "trips.txt",
            "stop_times.txt",
        }

    def list_files(self, archive_path: Path) -> set[str]:
        return self._files

    def read_csv(self, archive_path: Path, file_name: str) -> Iterator[dict[str, str]]:
        return iter([])

    def exists(self, archive_path: Path, file_name: str) -> bool:
        return file_name in self._files


class FakeGtfsImportService(GtfsImportService):
    def __init__(self) -> None:
        super().__init__(
            agency_repository=FakeAgencyRepository(),
            route_repository=FakeRouteRepository(),
            stop_repository=FakeStopRepository(),
            trip_repository=FakeTripRepository(),
            stoptime_repository=FakeStopTimeRepository(),
        )
        self.imported_count = 0
        self.last_schedule_version_id: int | None = None

    def import_all(
        self,
        archive_path: Path,
        reader: GtfsArchiveReader,
        schedule_version_id: int,
    ) -> dict[str, ImportStats]:
        self.imported_count += 1
        self.last_schedule_version_id = schedule_version_id
        return {
            "agencies": ImportStats(imported=1, rejected=0),
            "routes": ImportStats(imported=1, rejected=0),
            "stops": ImportStats(imported=1, rejected=0),
            "trips": ImportStats(imported=1, rejected=0),
            "stop_times": ImportStats(imported=1, rejected=0),
        }


class FakeContainer:
    def __init__(self) -> None:
        self.agency_repository = FakeAgencyRepository()
        self.route_repository = FakeRouteRepository()
        self.stop_repository = FakeStopRepository()
        self.trip_repository = FakeTripRepository()
        self.stoptime_repository = FakeStopTimeRepository()

        self.service = GtfsImportService(
            agency_repository=self.agency_repository,
            route_repository=self.route_repository,
            stop_repository=self.stop_repository,
            trip_repository=self.trip_repository,
            stoptime_repository=self.stoptime_repository,
        )


class FakeChecksumService(ChecksumService):
    def calculate_from_file(self, path: Path) -> str:
        return "a" * 64


class FakeFeedUploadContainer:
    def __init__(self, files: set[str] | None = None) -> None:
        self.schedule_version_repository = FakeScheduleVersionRepository()
        self.archive_reader = FakeGtfsArchiveReader(files)
        self.import_service = FakeGtfsImportService()
        self.checksum_service = FakeChecksumService()

        self.validator = FeedValidator()
        self.schedule_version_service = ScheduleVersionService(
            self.schedule_version_repository,
        )

        self.service = FeedUploadService(
            validator=self.validator,
            checksum_service=self.checksum_service,
            schedule_version_service=self.schedule_version_service,
            archive_reader=self.archive_reader,
            import_service=self.import_service,
        )


def get_service() -> FakeContainer:
    return FakeContainer()


def get_feed_upload_service(
    files: set[str] | None = None,
) -> FakeFeedUploadContainer:
    return FakeFeedUploadContainer(files)


class FakeNotificationRepository:
    def __init__(self) -> None:
        self.saved: list[Notification] = []

    def save(
        self,
        notification: Notification,
    ) -> Notification:
        if notification.id is None:
            notification = replace(notification, id=len(self.saved) + 1)
        self.saved.append(notification)
        return notification

    def find_by_user_id(
        self,
        user_id: int,
    ) -> list[Notification]:
        return [
            notification
            for notification in self.saved
            if notification.user_id == user_id
        ]

    def find_unread_by_user_id(
        self,
        user_id: int,
    ) -> list[Notification]:
        return [
            notification
            for notification in self.saved
            if notification.user_id == user_id and notification.is_unread
        ]


class FakeNotificationContainer:
    def __init__(self) -> None:
        self.notification_repository = FakeNotificationRepository()

        self.service = NotificationService(
            self.notification_repository,
        )


def get_notification_service() -> FakeNotificationContainer:
    return FakeNotificationContainer()


class FakeSubscriptionRepository:
    def __init__(self) -> None:
        self.saved: list[Subscription] = []
        self._next_id = 1

    def save(self, subscription: Subscription) -> Subscription:
        if subscription.id is None:
            existing = self.find_by_user_and_route(
                subscription.user_id, subscription.route_id
            )
            if existing is not None:
                raise AlreadySubscribedError(
                    subscription.user_id, subscription.route_id
                )
            subscription = replace(subscription, id=self._next_id)
            self._next_id += 1
        self.saved.append(subscription)
        return subscription

    def find_by_id(self, subscription_id: int) -> Subscription | None:
        return next(
            (s for s in self.saved if s.id == subscription_id),
            None,
        )

    def find_by_user_id(self, user_id: int) -> list[Subscription]:
        return [s for s in self.saved if s.user_id == user_id]

    def find_by_route_id(self, route_id: int) -> list[Subscription]:
        return [s for s in self.saved if s.route_id == route_id]

    def find_by_user_and_route(
        self,
        user_id: int,
        route_id: int,
    ) -> Subscription | None:
        return next(
            (s for s in self.saved if s.user_id == user_id and s.route_id == route_id),
            None,
        )

    def delete(self, subscription_id: int) -> None:
        self.saved = [s for s in self.saved if s.id != subscription_id]
