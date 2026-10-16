from sqlalchemy import select
from sqlalchemy.orm import Session

from transit_advisor.domain.agency import Agency
from transit_advisor.infrastructure.database.models.agency import (
    AgencyModel,
)


class SqlAlchemyAgencyRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def save(
        self,
        agency: Agency,
    ) -> Agency:
        agency_model = AgencyModel(
            agency_id=agency.agency_id,
            name=agency.name,
            timezone=agency.timezone,
            language=agency.language,
            phone=agency.phone,
            fare_url=agency.fare_url,
            email=agency.email,
        )

        self._session.add(agency_model)
        self._session.commit()
        self._session.refresh(agency_model)

        return Agency(
            id=agency_model.id,
            agency_id=agency_model.agency_id,
            name=agency_model.name,
            timezone=agency_model.timezone,
            language=agency_model.language,
            phone=agency_model.phone,
            fare_url=agency_model.fare_url,
            email=agency_model.email,
        )

    def find_by_agency_id(
        self,
        agency_id: str,
    ) -> Agency | None:
        statement = select(AgencyModel).where(
            AgencyModel.agency_id == agency_id,
        )

        agency_model = self._session.scalar(statement)

        if agency_model is None:
            return None

        return Agency(
            id=agency_model.id,
            agency_id=agency_model.agency_id,
            name=agency_model.name,
            timezone=agency_model.timezone,
            language=agency_model.language,
            phone=agency_model.phone,
            fare_url=agency_model.fare_url,
            email=agency_model.email,
        )
