from transit_advisor.domain.repositories.agency import AgencyRepository
from transit_advisor.domain.repositories.route import RouteRepository
from transit_advisor.infrastructure.gtfs.mappers.agency import to_agency
from transit_advisor.infrastructure.gtfs.mappers.route import to_route


class GtfsImportService:
    def __init__(
        self, agency_repository: AgencyRepository, route_repository: RouteRepository
    ) -> None:
        self._agency_repository = agency_repository
        self._route_repository = route_repository

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

    def import_routes(
        self,
        rows: list[dict[str, str]],
    ) -> int:
        imported = 0

        for row in rows:
            gtfs_agency_id = row.get(
                "agency_id",
                "",
            )

            agency = self._agency_repository.find_by_agency_id(
                gtfs_agency_id,
            )

            if agency is None:
                continue

            if agency.id is None:
                continue

            route = to_route(
                row=row,
                agency_id=agency.id,
            )

            if route is None:
                continue

            self._route_repository.save(
                route,
            )

            imported += 1

        return imported
