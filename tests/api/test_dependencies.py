from sqlalchemy.orm import Session

from transit_advisor.api.dependencies import (
    get_agency_repository,
    get_checksum_service,
    get_feed_upload_service,
    get_feed_validator,
    get_gtfs_import_service,
    get_notification_repository,
    get_notification_service,
    get_route_repository,
    get_schedule_update_service,
    get_schedule_version_repository,
    get_schedule_version_service,
    get_stop_repository,
    get_stoptime_repository,
    get_subscription_repository,
    get_subscription_service,
    get_trip_repository,
)
from transit_advisor.infrastructure.repositories.agency import (
    SqlAlchemyAgencyRepository,
)
from transit_advisor.infrastructure.repositories.notification import (
    SqlAlchemyNotificationRepository,
)
from transit_advisor.infrastructure.repositories.route import (
    SqlAlchemyRouteRepository,
)
from transit_advisor.infrastructure.repositories.scheduleversion import (
    SqlAlchemyScheduleVersionRepository,
)
from transit_advisor.infrastructure.repositories.stop import (
    SqlAlchemyStopRepository,
)
from transit_advisor.infrastructure.repositories.stoptime import (
    SqlAlchemyStopTimeRepository,
)
from transit_advisor.infrastructure.repositories.subscription import (
    SqlAlchemySubscriptionRepository,
)
from transit_advisor.infrastructure.repositories.trip import (
    SqlAlchemyTripRepository,
)
from transit_advisor.services.checksum_service import ChecksumService
from transit_advisor.services.feed_upload_service import FeedUploadService
from transit_advisor.services.feed_validation_service import FeedValidator
from transit_advisor.services.gtfs_import_service import GtfsImportService
from transit_advisor.services.notification_service import NotificationService
from transit_advisor.services.schedule_update_service import ScheduleUpdateService
from transit_advisor.services.schedule_version_service import ScheduleVersionService
from transit_advisor.services.subscription_service import SubscriptionService


def test_get_feed_validator() -> None:
    service = get_feed_validator()
    assert isinstance(service, FeedValidator)


def test_get_checksum_service() -> None:
    service = get_checksum_service()
    assert isinstance(service, ChecksumService)


def test_get_agency_repository(session: Session) -> None:
    repo = get_agency_repository(session)
    assert isinstance(repo, SqlAlchemyAgencyRepository)


def test_get_route_repository(session: Session) -> None:
    repo = get_route_repository(session)
    assert isinstance(repo, SqlAlchemyRouteRepository)


def test_get_stop_repository(session: Session) -> None:
    repo = get_stop_repository(session)
    assert isinstance(repo, SqlAlchemyStopRepository)


def test_get_trip_repository(session: Session) -> None:
    repo = get_trip_repository(session)
    assert isinstance(repo, SqlAlchemyTripRepository)


def test_get_stoptime_repository(session: Session) -> None:
    repo = get_stoptime_repository(session)
    assert isinstance(repo, SqlAlchemyStopTimeRepository)


def test_get_notification_repository(session: Session) -> None:
    repo = get_notification_repository(session)
    assert isinstance(repo, SqlAlchemyNotificationRepository)


def test_get_subscription_repository(session: Session) -> None:
    repo = get_subscription_repository(session)
    assert isinstance(repo, SqlAlchemySubscriptionRepository)


def test_get_schedule_version_repository(session: Session) -> None:
    repo = get_schedule_version_repository(session)
    assert isinstance(repo, SqlAlchemyScheduleVersionRepository)


def test_get_notification_service(session: Session) -> None:
    repository = get_notification_repository(session)
    service = get_notification_service(repository)
    assert isinstance(service, NotificationService)


def test_get_subscription_service(session: Session) -> None:
    subscription_repository = get_subscription_repository(session)
    route_repository = get_route_repository(session)
    service = get_subscription_service(
        repository=subscription_repository,
        route_repository=route_repository,
    )
    assert isinstance(service, SubscriptionService)


def test_get_schedule_version_service(session: Session) -> None:
    repository = get_schedule_version_repository(session)
    service = get_schedule_version_service(repository)
    assert isinstance(service, ScheduleVersionService)


def test_get_gtfs_import_service(session: Session) -> None:
    service = get_gtfs_import_service(
        agency_repository=get_agency_repository(session),
        route_repository=get_route_repository(session),
        stop_repository=get_stop_repository(session),
        trip_repository=get_trip_repository(session),
        stoptime_repository=get_stoptime_repository(session),
    )
    assert isinstance(service, GtfsImportService)


def test_get_schedule_update_service(session: Session) -> None:
    service = get_schedule_update_service(session)
    assert isinstance(service, ScheduleUpdateService)


def test_get_feed_upload_service(session: Session) -> None:
    service = get_feed_upload_service(
        validator=get_feed_validator(),
        checksum_service=get_checksum_service(),
        schedule_version_service=get_schedule_version_service(
            get_schedule_version_repository(session),
        ),
        import_service=get_gtfs_import_service(
            agency_repository=get_agency_repository(session),
            route_repository=get_route_repository(session),
            stop_repository=get_stop_repository(session),
            trip_repository=get_trip_repository(session),
            stoptime_repository=get_stoptime_repository(session),
        ),
    )
    assert isinstance(service, FeedUploadService)
