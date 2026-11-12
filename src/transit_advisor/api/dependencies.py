from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session, sessionmaker

from transit_advisor.infrastructure.archive.gtfs_archive_reader import GtfsArchiveReader
from transit_advisor.infrastructure.database.base import engine
from transit_advisor.infrastructure.repositories.agency import (
    SqlAlchemyAgencyRepository,
)
from transit_advisor.infrastructure.repositories.analytics import (
    SqlAlchemyAnalyticsRepository,
)
from transit_advisor.infrastructure.repositories.notification import (
    SqlAlchemyNotificationRepository,
)
from transit_advisor.infrastructure.repositories.route import SqlAlchemyRouteRepository
from transit_advisor.infrastructure.repositories.scheduleversion import (
    SqlAlchemyScheduleVersionRepository,
)
from transit_advisor.infrastructure.repositories.stop import SqlAlchemyStopRepository
from transit_advisor.infrastructure.repositories.stoptime import (
    SqlAlchemyStopTimeRepository,
)
from transit_advisor.infrastructure.repositories.subscription import (
    SqlAlchemySubscriptionRepository,
)
from transit_advisor.infrastructure.repositories.trip import SqlAlchemyTripRepository
from transit_advisor.services.analytics_service import AnalyticsService
from transit_advisor.services.checksum_service import ChecksumService
from transit_advisor.services.feed_upload_service import FeedUploadService
from transit_advisor.services.feed_validation_service import FeedValidator
from transit_advisor.services.gtfs_import_service import GtfsImportService
from transit_advisor.services.journey_service import JourneyService
from transit_advisor.services.notification_service import NotificationService
from transit_advisor.services.schedule_diff_service import ScheduleDiffService
from transit_advisor.services.schedule_update_service import ScheduleUpdateService
from transit_advisor.services.schedule_version_service import ScheduleVersionService
from transit_advisor.services.subscription_service import SubscriptionService

# TODO:
# Replace with SqlAlchemyScheduleVersionRepository
# when feed version persistence is fully integrated.

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_agency_repository(
    session: Annotated[Session, Depends(get_session)],
) -> SqlAlchemyAgencyRepository:
    return SqlAlchemyAgencyRepository(session)


def get_route_repository(
    session: Annotated[Session, Depends(get_session)],
) -> SqlAlchemyRouteRepository:
    return SqlAlchemyRouteRepository(session)


def get_stop_repository(
    session: Annotated[Session, Depends(get_session)],
) -> SqlAlchemyStopRepository:
    return SqlAlchemyStopRepository(session)


def get_trip_repository(
    session: Annotated[Session, Depends(get_session)],
) -> SqlAlchemyTripRepository:
    return SqlAlchemyTripRepository(session)


def get_stoptime_repository(
    session: Annotated[Session, Depends(get_session)],
) -> SqlAlchemyStopTimeRepository:
    return SqlAlchemyStopTimeRepository(session)


def get_gtfs_import_service(
    agency_repository: Annotated[
        SqlAlchemyAgencyRepository,
        Depends(get_agency_repository),
    ],
    route_repository: Annotated[
        SqlAlchemyRouteRepository,
        Depends(get_route_repository),
    ],
    stop_repository: Annotated[
        SqlAlchemyStopRepository,
        Depends(get_stop_repository),
    ],
    trip_repository: Annotated[
        SqlAlchemyTripRepository,
        Depends(get_trip_repository),
    ],
    stoptime_repository: Annotated[
        SqlAlchemyStopTimeRepository,
        Depends(get_stoptime_repository),
    ],
) -> GtfsImportService:
    return GtfsImportService(
        agency_repository=agency_repository,
        route_repository=route_repository,
        stop_repository=stop_repository,
        trip_repository=trip_repository,
        stoptime_repository=stoptime_repository,
    )


# Feed Upload Dependencies


def get_feed_validator() -> FeedValidator:
    return FeedValidator()


def get_checksum_service() -> ChecksumService:
    return ChecksumService()


def get_schedule_version_repository(
    session: Session = Depends(get_session),
) -> SqlAlchemyScheduleVersionRepository:
    return SqlAlchemyScheduleVersionRepository(session)


def get_schedule_version_service(
    repository: Annotated[
        SqlAlchemyScheduleVersionRepository,
        Depends(get_schedule_version_repository),
    ],
) -> ScheduleVersionService:
    return ScheduleVersionService(
        repository=repository,
    )


def get_schedule_update_service(
    session: Session = Depends(get_session),
) -> ScheduleUpdateService:
    return ScheduleUpdateService(
        diff_service=ScheduleDiffService(),
        notification_service=NotificationService(
            SqlAlchemyNotificationRepository(session),
        ),
        subscription_repository=SqlAlchemySubscriptionRepository(session),
        route_repository=SqlAlchemyRouteRepository(session),
        trip_repository=SqlAlchemyTripRepository(session),
        stoptime_repository=SqlAlchemyStopTimeRepository(session),
    )


def get_feed_upload_service(
    validator: Annotated[FeedValidator, Depends(get_feed_validator)],
    checksum_service: Annotated[ChecksumService, Depends(get_checksum_service)],
    schedule_version_service: Annotated[
        ScheduleVersionService,
        Depends(get_schedule_version_service),
    ],
    import_service: Annotated[
        GtfsImportService,
        Depends(get_gtfs_import_service),
    ],
) -> FeedUploadService:
    return FeedUploadService(
        validator=validator,
        checksum_service=checksum_service,
        schedule_version_service=schedule_version_service,
        archive_reader=GtfsArchiveReader(),
        import_service=import_service,
    )


# Notification Dependencies


def get_notification_repository(
    session: Annotated[
        Session,
        Depends(get_session),
    ],
) -> SqlAlchemyNotificationRepository:
    return SqlAlchemyNotificationRepository(
        session,
    )


def get_notification_service(
    repository: Annotated[
        SqlAlchemyNotificationRepository,
        Depends(get_notification_repository),
    ],
) -> NotificationService:
    return NotificationService(
        repository,
    )


def get_subscription_repository(
    session: Annotated[
        Session,
        Depends(get_session),
    ],
) -> SqlAlchemySubscriptionRepository:
    return SqlAlchemySubscriptionRepository(
        session,
    )


def get_subscription_service(
    repository: Annotated[
        SqlAlchemySubscriptionRepository,
        Depends(get_subscription_repository),
    ],
) -> SubscriptionService:
    return SubscriptionService(
        repository,
    )


def get_journey_service(
    stoptime_repository: Annotated[
        SqlAlchemyStopTimeRepository,
        Depends(get_stoptime_repository),
    ],
) -> JourneyService:
    return JourneyService(stoptime_repository)


def get_analytics_repository(
    session: Annotated[Session, Depends(get_session)],
) -> SqlAlchemyAnalyticsRepository:
    return SqlAlchemyAnalyticsRepository(session)


def get_analytics_service(
    repository: Annotated[
        SqlAlchemyAnalyticsRepository,
        Depends(get_analytics_repository),
    ],
) -> AnalyticsService:
    return AnalyticsService(repository)
