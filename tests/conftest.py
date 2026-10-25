import os
from collections.abc import Generator

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from transit_advisor.domain.agency import Agency
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
from transit_advisor.infrastructure.repositories.trip import SqlAlchemyTripRepository

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
