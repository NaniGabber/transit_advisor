from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.orm import Session, sessionmaker

from transit_advisor.domain.scheduleversion import ScheduleVersion
from transit_advisor.infrastructure.repositories.scheduleversion import (
    SqlAlchemyScheduleVersionRepository,
)
from transit_advisor.services.schedule_version_service import ScheduleVersionService


def test_concurrent_create_version_is_idempotent(
    session_factory: sessionmaker[Session],
) -> None:
    checksum = "a" * 64

    def create() -> ScheduleVersion | None:
        session = session_factory()
        try:
            service = ScheduleVersionService(
                SqlAlchemyScheduleVersionRepository(session),
            )
            version = service.create_version(checksum)
            session.commit()
            return version
        except Exception:
            session.rollback()
            return None
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create) for _ in range(10)]
        results = [f.result() for f in futures]

    assert len([r for r in results if r is not None]) == 1


def test_concurrent_import_is_idempotent(
    session_factory: sessionmaker[Session],
) -> None:
    from tests.conftest import make_zip
    from transit_advisor.infrastructure.archive.gtfs_archive_reader import (
        GtfsArchiveReader,
    )
    from transit_advisor.infrastructure.repositories.agency import (
        SqlAlchemyAgencyRepository,
    )
    from transit_advisor.infrastructure.repositories.route import (
        SqlAlchemyRouteRepository,
    )
    from transit_advisor.infrastructure.repositories.stop import (
        SqlAlchemyStopRepository,
    )
    from transit_advisor.infrastructure.repositories.stoptime import (
        SqlAlchemyStopTimeRepository,
    )
    from transit_advisor.infrastructure.repositories.trip import (
        SqlAlchemyTripRepository,
    )
    from transit_advisor.services.checksum_service import ChecksumService
    from transit_advisor.services.feed_upload_service import FeedUploadService
    from transit_advisor.services.feed_validation_service import FeedValidator
    from transit_advisor.services.gtfs_import_service import GtfsImportService

    content = make_zip(
        {
            "agency.txt": b"agency_id,agency_name,agency_timezone\n \
            agency_1,Metro,Europe/Kyiv\n",
            "routes.txt": b"route_id,agency_id,route_short_name\nroute_1,agency_1,11\n",
            "stops.txt": b"stop_id,stop_name\nstop_1,Central Station\n",
            "trips.txt": b"route_id,trip_id\nroute_1,trip_1\n",
            "stop_times.txt": (
                b"trip_id,arrival_time,departure_time,"
                b"stop_id,stop_sequence\n"
                b"trip_1,08:00:00,08:00:00,stop_1,1\n"
            ),
        }
    )

    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        tmp.write(content)
        archive_path = Path(tmp.name)

    def upload() -> int:
        session = session_factory()
        try:
            service = FeedUploadService(
                validator=FeedValidator(),
                checksum_service=ChecksumService(),
                schedule_version_service=ScheduleVersionService(
                    SqlAlchemyScheduleVersionRepository(session),
                ),
                archive_reader=GtfsArchiveReader(),
                import_service=GtfsImportService(
                    agency_repository=SqlAlchemyAgencyRepository(session),
                    route_repository=SqlAlchemyRouteRepository(session),
                    stop_repository=SqlAlchemyStopRepository(session),
                    trip_repository=SqlAlchemyTripRepository(session),
                    stoptime_repository=SqlAlchemyStopTimeRepository(session),
                ),
            )
            result = service.upload(archive_path)
            session.commit()
            if result.duplicate:
                return 409
            return 201
        except Exception:
            session.rollback()
            return -1
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(upload) for _ in range(10)]
        results = [f.result() for f in futures]

    archive_path.unlink(missing_ok=True)

    assert len(results) == 10, results
    assert results.count(201) == 1, results
    assert results.count(409) == 9, results

    session = session_factory()
    try:
        from transit_advisor.infrastructure.database.models.agency import AgencyModel
        from transit_advisor.infrastructure.database.models.scheduleversion import (
            ScheduleVersionModel,
        )

        assert session.query(ScheduleVersionModel).count() == 1
        assert session.query(AgencyModel).count() == 1
    finally:
        session.close()
