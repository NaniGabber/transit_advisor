from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session, sessionmaker

from transit_advisor.infrastructure.database.base import engine
from transit_advisor.infrastructure.repositories.in_memory_scheduleversion import (
    InMemoryScheduleVersionRepository,
)
from transit_advisor.infrastructure.repositories.notification import (
    SqlAlchemyNotificationRepository,
)
from transit_advisor.services.checksum_service import ChecksumService
from transit_advisor.services.feed_upload_service import FeedUploadService
from transit_advisor.services.feed_validation_service import FeedValidator
from transit_advisor.services.notification_service import (
    NotificationService,
)
from transit_advisor.services.schedule_version_service import ScheduleVersionService

_repository_singleton = InMemoryScheduleVersionRepository()


def get_feed_validator() -> FeedValidator:
    return FeedValidator()


def get_checksum_service() -> ChecksumService:
    return ChecksumService()


def get_schedule_version_repository() -> InMemoryScheduleVersionRepository:
    return _repository_singleton


def get_schedule_version_service(
    repository: Annotated[
        InMemoryScheduleVersionRepository, Depends(get_schedule_version_repository)
    ],
) -> ScheduleVersionService:
    return ScheduleVersionService(repository=repository)


def get_feed_upload_service(
    validator: Annotated[FeedValidator, Depends(get_feed_validator)],
    checksum_service: Annotated[ChecksumService, Depends(get_checksum_service)],
    schedule_version_service: Annotated[
        ScheduleVersionService, Depends(get_schedule_version_service)
    ],
) -> FeedUploadService:
    return FeedUploadService(
        validator=validator,
        checksum_service=checksum_service,
        schedule_version_service=schedule_version_service,
    )


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


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
