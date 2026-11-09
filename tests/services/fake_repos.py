from collections.abc import Iterator
from dataclasses import replace
from datetime import time
from pathlib import Path

from transit_advisor.domain.agency import Agency
from transit_advisor.domain.notification import Notification
from transit_advisor.domain.route import Route
from transit_advisor.domain.scheduleversion import ScheduleVersion
from transit_advisor.domain.stop import Stop
from transit_advisor.domain.stoptime import StopTime
from transit_advisor.domain.subscription import Subscription
from transit_advisor.domain.trip import Trip
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
            # Для юніт-тестів зазвичай повертаємо порожній список,
            # якщо не передано спеціальний мапінг.
            results = []

        return results[offset : offset + limit]

    def find_by_id(self, route_pk: int) -> Route | None:
        return next((r for r in self.saved if r.id == route_pk), None)

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
            # Для юніт-тестів зазвичай повертаємо порожній список,
            # якщо не передано спеціальний мапінг.
            results = []

        return results[offset : offset + limit]


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
        self._next_id = 1

    def save(self, trip: Trip) -> Trip:
        if trip.id is None:
            trip = replace(trip, id=self._next_id)
            self._next_id += 1
        self.saved.append(trip)
        return trip

    def find_by_trip_id(self, trip_id: str) -> Trip | None:
        return next((t for t in self.saved if t.trip_id == trip_id), None)

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

    def find_by_trip_id(self, trip_id: int) -> list[StopTime]:
        return [st for st in self.saved if st.trip_id == trip_id]

    def find_by_trip_ids(self, trip_ids: list[int]) -> list[StopTime]:
        return [st for st in self.saved if st.trip_id in trip_ids]

    def find_by_stop_id(self, stop_id: int) -> list[StopTime]:
        return [st for st in self.saved if st.stop_id == stop_id]

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


class FakeScheduleVersionRepository:
    def __init__(self) -> None:
        self.saved: list[ScheduleVersion] = []

    def save(
        self,
        version: ScheduleVersion,
    ) -> ScheduleVersion:
        if version.id is None:
            version.id = len(self.saved) + 1

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
        self.imported_count = 0
        self.last_schedule_version_id: int | None = None

    def import_all(
        self,
        archive_path: Path,
        reader: GtfsArchiveReader,
        schedule_version_id: int,
    ) -> dict[str, int]:
        self.imported_count += 1
        self.last_schedule_version_id = schedule_version_id
        return {"agencies": 1, "routes": 1, "stops": 1, "trips": 1, "stop_times": 1}


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
        self.checksum_service = FakeChecksumService()  # <-- Додано

        self.validator = FeedValidator()
        self.schedule_version_service = ScheduleVersionService(
            self.schedule_version_repository,
        )

        self.service = FeedUploadService(
            validator=self.validator,
            checksum_service=self.checksum_service,  # <-- Використовуємо фейк
            schedule_version_service=self.schedule_version_service,
            archive_reader=self.archive_reader,
            import_service=self.import_service,
        )


def get_service() -> FakeContainer:
    return FakeContainer()


def get_feed_upload_service(files: set[str] | None = None) -> FakeFeedUploadContainer:
    return FakeFeedUploadContainer(files)


class FakeNotificationRepository:
    def __init__(self) -> None:
        self.saved: list[Notification] = []

    def save(
        self,
        notification: Notification,
    ) -> Notification:
        if notification.id is None:
            notification.id = len(self.saved) + 1

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

    def save(
        self,
        subscription: Subscription,
    ) -> Subscription:
        if subscription.id is None:
            subscription.id = len(self.saved) + 1

        self.saved.append(subscription)

        return subscription

    def find_by_route_id(
        self,
        route_id: int,
    ) -> list[Subscription]:
        return [
            subscription
            for subscription in self.saved
            if subscription.route_id == route_id
        ]

    def find_by_user_id(
        self,
        user_id: int,
    ) -> list[Subscription]:
        return [
            subscription
            for subscription in self.saved
            if subscription.user_id == user_id
        ]
