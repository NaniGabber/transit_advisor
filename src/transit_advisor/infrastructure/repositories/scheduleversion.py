from sqlalchemy import select
from sqlalchemy.orm import Session

from transit_advisor.domain.scheduleversion import (
    ScheduleVersion,
)
from transit_advisor.infrastructure.database.models.scheduleversion import (
    ScheduleVersionModel,
)


class SqlAlchemyScheduleVersionRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def save(
        self,
        version: ScheduleVersion,
    ) -> ScheduleVersion:
        version_model = ScheduleVersionModel(
            checksum=version.checksum,
            imported_at=version.imported_at,
        )

        self._session.add(version_model)
        self._session.commit()
        self._session.refresh(version_model)

        return ScheduleVersion(
            id=version_model.id,
            checksum=version_model.checksum,
            imported_at=version_model.imported_at,
        )

    def find_by_checksum(
        self,
        checksum: str,
    ) -> ScheduleVersion | None:
        statement = select(
            ScheduleVersionModel,
        ).where(
            ScheduleVersionModel.checksum == checksum,
        )

        version_model = self._session.scalar(
            statement,
        )

        if version_model is None:
            return None

        return ScheduleVersion(
            id=version_model.id,
            checksum=version_model.checksum,
            imported_at=version_model.imported_at,
        )
