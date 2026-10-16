from transit_advisor.domain.repositories.agency import AgencyRepository
from transit_advisor.infrastructure.gtfs.mappers.agency import (
    to_agency,
)


class GtfsImportService:
    def __init__(self, agency_repository: AgencyRepository) -> None:
        self._agency_repository = agency_repository

    def import_agencies(
        self,
        rows: list[dict[str, str]],
    ) -> int:
        imported = 0

        for row in rows:
            agency = to_agency(row)

            if agency is None:
                continue

            self._agency_repository.save(agency)
            imported += 1

        return imported
