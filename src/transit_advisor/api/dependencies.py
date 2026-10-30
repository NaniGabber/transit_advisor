from typing import Annotated

from fastapi import Depends

from transit_advisor.infrastructure.repositories.in_memory_scheduleversion import (
    InMemoryScheduleVersionRepository,
)
from transit_advisor.services.checksum_service import ChecksumService
from transit_advisor.services.feed_upload_service import FeedUploadService
from transit_advisor.services.feed_validation_service import FeedValidator
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
