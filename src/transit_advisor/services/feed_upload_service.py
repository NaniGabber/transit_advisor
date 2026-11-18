import logging
from pathlib import Path

from transit_advisor.domain.upload_result import UploadResult
from transit_advisor.infrastructure.archive.gtfs_archive_reader import (
    GtfsArchiveReader,
)
from transit_advisor.services.checksum_service import ChecksumService
from transit_advisor.services.feed_validation_service import FeedValidator
from transit_advisor.services.gtfs_import_service import GtfsImportService
from transit_advisor.services.schedule_update_service import ScheduleUpdateService
from transit_advisor.services.schedule_version_service import ScheduleVersionService

logger = logging.getLogger(__name__)


class FeedUploadService:
    def __init__(
        self,
        validator: FeedValidator,
        checksum_service: ChecksumService,
        schedule_version_service: ScheduleVersionService,
        archive_reader: GtfsArchiveReader,
        import_service: GtfsImportService,
        schedule_update_service: ScheduleUpdateService | None = None,
    ) -> None:
        self._validator = validator
        self._checksum_service = checksum_service
        self._schedule_version_service = schedule_version_service
        self._archive_reader = archive_reader
        self._import_service = import_service
        self._schedule_update_service = schedule_update_service

    def upload(self, archive_path: Path) -> UploadResult:
        archive_files = self._archive_reader.list_files(archive_path)

        if not self._validator.validate(archive_files):
            logger.warning(
                "feed_upload_rejected reason=missing_required_files files=%s",
                sorted(archive_files),
            )
            return UploadResult(imported=False, duplicate=False, checksum="")

        checksum = self._checksum_service.calculate_from_file(archive_path)

        previous_version = self._schedule_version_service.find_latest()
        old_version_id = previous_version.id if previous_version else None

        version = self._schedule_version_service.create_version(checksum)
        if version is None:
            logger.warning("duplicate_feed checksum=%s", checksum)
            return UploadResult(imported=False, duplicate=True, checksum=checksum)

        if version.id is None:
            raise RuntimeError("ScheduleVersion was saved without an id")

        stats = self._import_service.import_all(
            archive_path,
            self._archive_reader,
            schedule_version_id=version.id,
        )

        if self._schedule_update_service is not None and old_version_id is not None:
            notifications_created = (
                self._schedule_update_service.process_version_update(
                    old_version_id=old_version_id,
                    new_version_id=version.id,
                    schedule_version_id=version.id,
                )
            )
            logger.info(
                "schedule_update_processed old_version_id=%s "
                "new_version_id=%s notifications=%s",
                old_version_id,
                version.id,
                notifications_created,
            )

        imported_total = sum(stat.imported for stat in stats.values())
        rejected_total = sum(stat.rejected for stat in stats.values())
        logger.info(
            "feed_uploaded version_id=%s checksum=%s imported=%s rejected=%s tables=%s",
            version.id,
            checksum,
            imported_total,
            rejected_total,
            {name: stat.imported for name, stat in stats.items()},
        )
        if rejected_total:
            logger.warning(
                "feed_rows_rejected version_id=%s rejected=%s",
                version.id,
                rejected_total,
            )

        return UploadResult(
            imported=True,
            duplicate=False,
            checksum=checksum,
            stats=stats,
        )
