from transit_advisor.domain.agency import Agency
from transit_advisor.services.gtfs_import_service import GtfsImportService


class FakeAgencyRepository:
    def __init__(self) -> None:
        self.saved: list[Agency] = []

    def save(
        self,
        agency: Agency,
    ) -> Agency:
        self.saved.append(agency)
        return agency

    def find_by_agency_id(
        self,
        agency_id: str,
    ) -> Agency | None:
        for agency in self.saved:
            if agency.agency_id == agency_id:
                return agency

        return None


def test_import_agencies_returns_imported_count() -> None:
    repository = FakeAgencyRepository()

    service = GtfsImportService(agency_repository=repository)

    rows = [
        {
            "agency_id": "metro",
            "agency_name": "Kharkiv Metro",
            "agency_timezone": "Europe/Kyiv",
        }
    ]

    imported = service.import_agencies(rows)

    assert imported == 1


def test_import_agencies_saves_valid_agencies() -> None:
    repository = FakeAgencyRepository()

    service = GtfsImportService(
        agency_repository=repository,
    )

    rows = [
        {
            "agency_id": "metro",
            "agency_name": "Kharkiv Metro",
            "agency_timezone": "Europe/Kyiv",
        }
    ]

    service.import_agencies(rows)

    assert len(repository.saved) == 1

    agency = repository.saved[0]

    assert agency.agency_id == "metro"
    assert agency.name == "Kharkiv Metro"


def test_import_agencies_skips_invalid_rows() -> None:
    repository = FakeAgencyRepository()

    service = GtfsImportService(
        agency_repository=repository,
    )

    rows = [
        {
            "agency_id": "",
            "agency_name": "Kharkiv Metro",
            "agency_timezone": "Europe/Kyiv",
        }
    ]

    imported = service.import_agencies(rows)

    assert imported == 0
    assert len(repository.saved) == 0
