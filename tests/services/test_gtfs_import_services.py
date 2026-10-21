from transit_advisor.domain.agency import Agency
from transit_advisor.services.gtfs_import_service import GtfsImportService

from .fake_repos import FakeAgencyRepository, FakeRouteRepository


def test_import_agencies_returns_imported_count() -> None:
    agency_repository = FakeAgencyRepository()
    route_repository = FakeRouteRepository()

    service = GtfsImportService(
        agency_repository=agency_repository,
        route_repository=route_repository,
    )

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
    agency_repository = FakeAgencyRepository()
    route_repository = FakeRouteRepository()

    service = GtfsImportService(
        agency_repository=agency_repository,
        route_repository=route_repository,
    )

    rows = [
        {
            "agency_id": "metro",
            "agency_name": "Kharkiv Metro",
            "agency_timezone": "Europe/Kyiv",
        }
    ]

    service.import_agencies(rows)

    assert len(agency_repository.saved) == 1

    agency = agency_repository.saved[0]

    assert agency.agency_id == "metro"
    assert agency.name == "Kharkiv Metro"


def test_import_agencies_skips_invalid_rows() -> None:
    agency_repository = FakeAgencyRepository()
    route_repository = FakeRouteRepository()

    service = GtfsImportService(
        agency_repository=agency_repository,
        route_repository=route_repository,
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
    assert len(agency_repository.saved) == 0


def test_import_routes_returns_imported_count() -> None:
    agency_repository = FakeAgencyRepository()
    route_repository = FakeRouteRepository()

    agency_repository.save(
        Agency(
            id=1,
            agency_id="metro",
            name="Kharkiv Metro",
            timezone="Europe/Kyiv",
        )
    )

    service = GtfsImportService(
        agency_repository=agency_repository,
        route_repository=route_repository,
    )

    rows = [
        {
            "agency_id": "metro",
            "route_id": "11",
            "route_short_name": "11",
            "route_long_name": "Railway Station",
            "route_type": "3",
        }
    ]

    imported = service.import_routes(rows)

    assert imported == 1


def test_import_routes_saves_valid_route() -> None:
    agency_repository = FakeAgencyRepository()
    route_repository = FakeRouteRepository()

    agency_repository.save(
        Agency(
            id=1,
            agency_id="metro",
            name="Kharkiv Metro",
            timezone="Europe/Kyiv",
        )
    )

    service = GtfsImportService(
        agency_repository=agency_repository,
        route_repository=route_repository,
    )

    rows = [
        {
            "agency_id": "metro",
            "route_id": "11",
            "route_short_name": "11",
            "route_long_name": "Railway Station",
            "route_type": "3",
        }
    ]

    service.import_routes(rows)

    assert len(route_repository.saved) == 1
    assert route_repository.saved[0].route_id == "11"


def test_import_routes_skips_unknown_agency() -> None:
    agency_repository = FakeAgencyRepository()
    route_repository = FakeRouteRepository()

    service = GtfsImportService(
        agency_repository=agency_repository,
        route_repository=route_repository,
    )

    rows = [
        {
            "agency_id": "unknown",
            "route_id": "11",
            "route_short_name": "11",
            "route_long_name": "Railway Station",
            "route_type": "3",
        }
    ]

    imported = service.import_routes(rows)

    assert imported == 0
    assert len(route_repository.saved) == 0


def test_import_routes_skips_invalid_route() -> None:
    agency_repository = FakeAgencyRepository()
    route_repository = FakeRouteRepository()

    agency_repository.save(
        Agency(
            id=1,
            agency_id="metro",
            name="Kharkiv Metro",
            timezone="Europe/Kyiv",
        )
    )

    service = GtfsImportService(
        agency_repository=agency_repository,
        route_repository=route_repository,
    )

    rows = [
        {
            "agency_id": "metro",
            "route_id": "",
            "route_short_name": "11",
            "route_long_name": "Railway Station",
            "route_type": "3",
        }
    ]

    imported = service.import_routes(rows)

    assert imported == 0
    assert len(route_repository.saved) == 0


def test_import_routes_imports_only_valid_routes() -> None:
    agency_repository = FakeAgencyRepository()
    route_repository = FakeRouteRepository()

    agency_repository.save(
        Agency(
            id=1,
            agency_id="metro",
            name="Kharkiv Metro",
            timezone="Europe/Kyiv",
        )
    )

    service = GtfsImportService(
        agency_repository=agency_repository,
        route_repository=route_repository,
    )

    rows = [
        {
            "agency_id": "metro",
            "route_id": "11",
            "route_short_name": "11",
            "route_long_name": "Railway Station",
            "route_type": "3",
        },
        {
            "agency_id": "missing",
            "route_id": "12",
            "route_short_name": "12",
            "route_long_name": "City Center",
            "route_type": "3",
        },
        {
            "agency_id": "metro",
            "route_id": "",
            "route_short_name": "13",
            "route_long_name": "Invalid",
            "route_type": "3",
        },
    ]

    imported = service.import_routes(rows)

    assert imported == 1
    assert len(route_repository.saved) == 1
