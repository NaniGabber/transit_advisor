from sqlalchemy import select
from sqlalchemy.orm import Session

from transit_advisor.domain.agency import Agency
from transit_advisor.infrastructure.database.models.agency import AgencyModel


class SqlAlchemyAgencyRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def save(self, agency: Agency) -> Agency:
        model = self._to_model(agency)
        self._session.add(model)
        self._session.flush()
        return self._to_domain(model)

    def save_all(self, agencies: list[Agency]) -> list[Agency]:
        """Bulk insert — один INSERT на весь батч."""
        if not agencies:
            return []
        models = [self._to_model(a) for a in agencies]
        self._session.add_all(models)
        self._session.flush()
        return [self._to_domain(m) for m in models]

    def find_by_agency_id(self, agency_id: str) -> Agency | None:
        statement = select(AgencyModel).where(
            AgencyModel.agency_id == agency_id,
        )
        model = self._session.scalar(statement)
        if model is None:
            return None
        return self._to_domain(model)

    def find_by_agency_ids(self, agency_ids: list[str]) -> dict[str, Agency]:
        """Bulk lookup. Один SELECT, повертає dict для O(1) доступу."""
        if not agency_ids:
            return {}
        statement = select(AgencyModel).where(
            AgencyModel.agency_id.in_(agency_ids),
        )
        return {
            m.agency_id: self._to_domain(m) for m in self._session.scalars(statement)
        }

    def _to_model(self, agency: Agency) -> AgencyModel:
        return AgencyModel(
            agency_id=agency.agency_id,
            name=agency.name,
            timezone=agency.timezone,
            language=agency.language,
            phone=agency.phone,
            fare_url=agency.fare_url,
            email=agency.email,
        )

    def _to_domain(self, model: AgencyModel) -> Agency:
        return Agency(
            id=model.id,
            agency_id=model.agency_id,
            name=model.name,
            timezone=model.timezone,
            language=model.language,
            phone=model.phone,
            fare_url=model.fare_url,
            email=model.email,
        )
