import io
import os
import zipfile
from collections.abc import Callable, Generator
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from tests.services.fake_repos import FakeNotificationRepository
from transit_advisor.api.dependencies import (
    get_feed_upload_service,
    get_notification_repository,
)
from transit_advisor.api.feeds import router as feeds_router
from transit_advisor.api.notification import router as notifications_router
from transit_advisor.domain.agency import Agency
from transit_advisor.domain.route import Route
from transit_advisor.infrastructure.database.base import Base
from transit_advisor.infrastructure.repositories.agency import (
    SqlAlchemyAgencyRepository,
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
from transit_advisor.infrastructure.repositories.subscription import (
    SqlAlchemySubscriptionRepository,
)
from transit_advisor.infrastructure.repositories.trip import SqlAlchemyTripRepository
from transit_advisor.services.checksum_service import ChecksumService
from transit_advisor.services.feed_upload_service import FeedUploadService
from transit_advisor.services.feed_validation_service import FeedValidator
from transit_advisor.services.schedule_version_service import ScheduleVersionService

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)

TestSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
def session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)

    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()

        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def agency_repository(
    session: Session,
) -> SqlAlchemyAgencyRepository:
    return SqlAlchemyAgencyRepository(
        session,
    )


@pytest.fixture
def agency(
    agency_repository: SqlAlchemyAgencyRepository,
) -> Agency:
    return agency_repository.save(
        Agency(
            id=None,
            agency_id="metro",
            name="Kharkiv Metro",
            timezone="Europe/Kyiv",
        )
    )


@pytest.fixture
def route_repository(
    session: Session,
) -> SqlAlchemyRouteRepository:
    return SqlAlchemyRouteRepository(
        session,
    )


@pytest.fixture
def stop_repository(
    session: Session,
) -> SqlAlchemyStopRepository:
    return SqlAlchemyStopRepository(
        session,
    )


@pytest.fixture
def trip_repository(
    session: Session,
) -> SqlAlchemyTripRepository:
    return SqlAlchemyTripRepository(session)


@pytest.fixture
def schedule_version_repository(
    session: Session,
) -> SqlAlchemyScheduleVersionRepository:
    return SqlAlchemyScheduleVersionRepository(
        session,
    )


def make_zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


@pytest.fixture
def feed_upload_service(
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
) -> FeedUploadService:
    return FeedUploadService(
        validator=FeedValidator(),
        checksum_service=ChecksumService(),
        schedule_version_service=ScheduleVersionService(
            repository=schedule_version_repository,
        ),
    )


@pytest.fixture
def app(feed_upload_service: FeedUploadService) -> Generator[FastAPI, None, None]:
    app = FastAPI()
    app.include_router(feeds_router)
    app.include_router(notifications_router)
    app.dependency_overrides[get_feed_upload_service] = lambda: feed_upload_service
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture
def subscription_repository(
    session: Session,
) -> SqlAlchemySubscriptionRepository:
    return SqlAlchemySubscriptionRepository(
        session,
    )


@pytest.fixture
def notification_repository(
    app: FastAPI,
) -> Generator[FakeNotificationRepository, None, None]:
    repo = FakeNotificationRepository()
    app.dependency_overrides[get_notification_repository] = lambda: repo
    try:
        yield repo
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def route(agency: Agency, route_repository: SqlAlchemyRouteRepository) -> Route:
    if agency.id is None:
        pytest.skip("agency not saved")
    return route_repository.save(
        Route(
            id=None,
            agency_id=agency.id,
            route_id="11",
            short_name="11",
            long_name="Railway Station",
            route_type=3,
        )
    )


@pytest.fixture
def archive_path(
    tmp_path: Path,
) -> Path:
    path = tmp_path / "feed.zip"

    with zipfile.ZipFile(
        path,
        "w",
    ) as archive:
        archive.writestr(
            "agency.txt",
            ("agency_id,agency_name\nmetro,Kharkiv Metro\n"),
        )

        archive.writestr(
            "routes.txt",
            ("route_id,route_short_name\n11,11\n15,15\n"),
        )

        archive.writestr(
            "stops.txt",
            ("stop_id,stop_name\n1,Station\n2,Center\n"),
        )

        archive.writestr(
            "trips.txt",
            ("route_id,trip_id\n11,trip_1\n"),
        )

        archive.writestr(
            "stop_times.txt",
            (
                "trip_id,arrival_time,departure_time,"
                "stop_id,stop_sequence\n"
                "trip_1,08:00:00,08:01:00,1,1\n"
            ),
        )

    return path


@pytest.fixture
def route_factory(
    route_repository: SqlAlchemyRouteRepository,
    agency: Agency,
) -> Callable[[str], Route]:
    def create(route_id: str) -> Route:
        assert agency.id is not None

        return route_repository.save(
            Route(
                id=None,
                agency_id=agency.id,
                route_id=route_id,
                short_name=route_id,
                long_name=f"Route {route_id}",
                route_type=3,
            )
        )

    return create
