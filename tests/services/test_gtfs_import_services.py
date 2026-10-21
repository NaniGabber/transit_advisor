from transit_advisor.domain.agency import Agency
from transit_advisor.services.gtfs_import_service import GtfsImportService

# Імпортуємо функцію, яка повертає контейнер
from .fake_repos import get_service


def test_import_agencies_returns_imported_count() -> None:
    container = get_service()
    rows = [
        {
            "agency_id": "metro",
            "agency_name": "Kharkiv Metro",
            "agency_timezone": "Europe/Kyiv",
        }
    ]

    imported = container.service.import_agencies(rows)

    assert imported == 1


def test_import_agencies_saves_valid_agencies() -> None:
    container = get_service()
    rows = [
        {
            "agency_id": "metro",
            "agency_name": "Kharkiv Metro",
            "agency_timezone": "Europe/Kyiv",
        }
    ]

    container.service.import_agencies(rows)

    # Тепер ми маємо доступ до сховища через container
    assert len(container.agency_repository.saved) == 1
    agency = container.agency_repository.saved[0]

    assert agency.agency_id == "metro"
    assert agency.name == "Kharkiv Metro"


def test_import_agencies_skips_invalid_rows() -> None:
    container = get_service()
    rows = [
        {
            "agency_id": "",
            "agency_name": "Kharkiv Metro",
            "agency_timezone": "Europe/Kyiv",
        }
    ]

    imported = container.service.import_agencies(rows)

    assert imported == 0
    assert len(container.agency_repository.saved) == 0


# --- Допоміжна функція для тестів маршрутів, щоб не дублювати код ---
def _get_service_with_agency() -> GtfsImportService:
    container = get_service()
    # Додаємо агентство в сховище заздалегідь
    container.agency_repository.save(
        Agency(
            id=1,
            agency_id="metro",
            name="Kharkiv Metro",
            timezone="Europe/Kyiv",
        )
    )
    return container.service


def test_import_routes_returns_imported_count() -> None:
    service = _get_service_with_agency()
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
    container = get_service()
    container.agency_repository.save(
        Agency(id=1, agency_id="metro", name="Kharkiv Metro", timezone="Europe/Kyiv")
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

    container.service.import_routes(rows)

    assert len(container.route_repository.saved) == 1
    assert container.route_repository.saved[0].route_id == "11"


def test_import_routes_skips_unknown_agency() -> None:
    container = get_service()

    rows = [
        {
            "agency_id": "unknown",
            "route_id": "11",
            "route_short_name": "11",
            "route_long_name": "Railway Station",
            "route_type": "3",
        }
    ]

    imported = container.service.import_routes(rows)

    assert imported == 0
    assert len(container.route_repository.saved) == 0


def test_import_routes_skips_invalid_route() -> None:
    container = get_service()
    container.agency_repository.save(
        Agency(id=1, agency_id="metro", name="Kharkiv Metro", timezone="Europe/Kyiv")
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

    imported = container.service.import_routes(rows)

    assert imported == 0
    assert len(container.route_repository.saved) == 0


def test_import_routes_imports_only_valid_routes() -> None:
    container = get_service()
    container.agency_repository.save(
        Agency(id=1, agency_id="metro", name="Kharkiv Metro", timezone="Europe/Kyiv")
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

    imported = container.service.import_routes(rows)

    assert imported == 1
    assert len(container.route_repository.saved) == 1


def test_import_stops_returns_imported_count() -> None:
    container = get_service()
    rows = [
        {
            "stop_id": "S1",
            "stop_name": "Railway Station",
            "stop_lat": "49.989",
            "stop_lon": "36.230",
        }
    ]

    imported = container.service.import_stops(rows)

    assert imported == 1


def test_import_stops_saves_valid_stop() -> None:
    container = get_service()
    rows = [
        {
            "stop_id": "S1",
            "stop_name": "Railway Station",
            "stop_lat": "49.989",
            "stop_lon": "36.230",
            "stop_code": "123",
            "stop_desc": "Main station",
        }
    ]

    container.service.import_stops(rows)

    assert len(container.stop_repository.saved) == 1
    stop = container.stop_repository.saved[0]

    assert stop.stop_id == "S1"
    assert stop.name == "Railway Station"
    assert stop.latitude == 49.989
    assert stop.longitude == 36.230
    assert stop.code == "123"
    assert stop.description == "Main station"


def test_import_stops_skips_invalid_row_missing_id() -> None:
    container = get_service()
    rows = [
        {
            "stop_id": "",  # Порожній ID
            "stop_name": "Railway Station",
            "stop_lat": "49.989",
            "stop_lon": "36.230",
        }
    ]

    imported = container.service.import_stops(rows)

    assert imported == 0
    assert len(container.stop_repository.saved) == 0


def test_import_stops_skips_invalid_row_missing_coordinates() -> None:
    container = get_service()
    rows = [
        {
            "stop_id": "S2",
            "stop_name": "Unknown Place",
            "stop_lat": "",  # Немає широти
            "stop_lon": "36.230",
        }
    ]

    imported = container.service.import_stops(rows)

    assert imported == 0
    assert len(container.stop_repository.saved) == 0


def test_import_stops_imports_only_valid_stops() -> None:
    container = get_service()
    rows = [
        {
            "stop_id": "S1",
            "stop_name": "Valid Stop",
            "stop_lat": "49.989",
            "stop_lon": "36.230",
        },
        {
            "stop_id": "",  # Невалідний (немає ID)
            "stop_name": "Invalid Stop",
            "stop_lat": "49.989",
            "stop_lon": "36.230",
        },
        {
            "stop_id": "S3",
            "stop_name": "Another Valid Stop",
            "stop_lat": "50.000",
            "stop_lon": "36.200",
        },
    ]

    imported = container.service.import_stops(rows)

    assert imported == 2
    assert len(container.stop_repository.saved) == 2
    assert container.stop_repository.saved[0].stop_id == "S1"
    assert container.stop_repository.saved[1].stop_id == "S3"
