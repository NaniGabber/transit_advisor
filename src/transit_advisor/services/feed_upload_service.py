from pathlib import Path

from transit_advisor.domain.upload_result import UploadResult
from transit_advisor.infrastructure.archive.gtfs_archive_reader import (
    GtfsArchiveReader,
)
from transit_advisor.services.checksum_service import ChecksumService
from transit_advisor.services.feed_validation_service import FeedValidator
from transit_advisor.services.gtfs_import_service import GtfsImportService
from transit_advisor.services.schedule_version_service import ScheduleVersionService


class FeedUploadService:
    def __init__(
        self,
        validator: FeedValidator,
        checksum_service: ChecksumService,
        schedule_version_service: ScheduleVersionService,
        archive_reader: GtfsArchiveReader,
        import_service: GtfsImportService,
    ) -> None:
        self._validator = validator
        self._checksum_service = checksum_service
        self._schedule_version_service = schedule_version_service
        self._archive_reader = archive_reader
        self._import_service = import_service

    def upload(self, archive_path: Path) -> UploadResult:
        archive_files = self._archive_reader.list_files(archive_path)

        if not self._validator.validate(archive_files):
            return UploadResult(imported=False, duplicate=False, checksum="")

        checksum = self._checksum_service.calculate_from_file(archive_path)

        version = self._schedule_version_service.create_version(checksum)
        if version is None:
            return UploadResult(imported=False, duplicate=True, checksum=checksum)

        if version.id is None:
            raise RuntimeError("ScheduleVersion was saved without an id")

        stats = self._import_service.import_all(
            archive_path,
            self._archive_reader,
            schedule_version_id=version.id,
        )

        return UploadResult(
            imported=True,
            duplicate=False,
            checksum=checksum,
            stats=stats,
        )
