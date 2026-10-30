from transit_advisor.domain.upload_result import UploadResult

from .checksum_service import ChecksumService
from .feed_validation_service import FeedValidator
from .schedule_version_service import ScheduleVersionService


class FeedUploadService:
    def __init__(
        self,
        validator: FeedValidator,
        checksum_service: ChecksumService,
        schedule_version_service: ScheduleVersionService,
    ) -> None:
        self._validator = validator
        self._checksum_service = checksum_service
        self._schedule_version_service = schedule_version_service

    def upload(
        self,
        archive_bytes: bytes,
        archive_files: set[str],
    ) -> UploadResult:
        if not self._validator.validate(archive_files):
            return UploadResult(
                imported=False,
                duplicate=False,
                checksum="",
            )

        checksum = self._checksum_service.calculate(archive_bytes)

        version = self._schedule_version_service.create_version(checksum)

        if version is None:
            return UploadResult(
                imported=False,
                duplicate=True,
                checksum=checksum,
            )

        return UploadResult(
            imported=True,
            duplicate=False,
            checksum=checksum,
        )
