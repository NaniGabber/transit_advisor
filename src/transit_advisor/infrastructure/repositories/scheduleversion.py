from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from transit_advisor.domain.exceptions import DuplicateScheduleVersionError
from transit_advisor.domain.scheduleversion import ScheduleVersion
from transit_advisor.infrastructure.database.models.scheduleversion import (
    ScheduleVersionModel,
)


class SqlAlchemyScheduleVersionRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def save(self, version: ScheduleVersion) -> ScheduleVersion:
        model = ScheduleVersionModel(
            checksum=version.checksum,
            imported_at=version.imported_at,
        )
        self._session.add(model)
        try:
            self._session.flush()
        except IntegrityError as exc:
            raise DuplicateScheduleVersionError(version.checksum) from exc
        return self._to_domain(model)

    def find_by_checksum(self, checksum: str) -> ScheduleVersion | None:
        statement = select(ScheduleVersionModel).where(
            ScheduleVersionModel.checksum == checksum,
        )

        version_model = self._session.scalar(statement)

        if version_model is None:
            return None

        return self._to_domain(version_model)

    def _to_domain(self, model: ScheduleVersionModel) -> ScheduleVersion:
        return ScheduleVersion(
            id=model.id,
            checksum=model.checksum,
            imported_at=model.imported_at,
        )
