import os
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from transit_advisor.infrastructure.database.base import Base
from transit_advisor.infrastructure.repositories.agency import (
    SqlAlchemyAgencyRepository,
)
from transit_advisor.infrastructure.repositories.route import (
    SqlAlchemyRouteRepository,
)

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
def route_repository(
    session: Session,
) -> SqlAlchemyRouteRepository:
    return SqlAlchemyRouteRepository(
        session,
    )
