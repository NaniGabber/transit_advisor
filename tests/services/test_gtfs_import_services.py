from transit_advisor.domain.agency import Agency
from transit_advisor.domain.route import Route
from transit_advisor.domain.stop import Stop
from transit_advisor.domain.trip import Trip
from transit_advisor.services.gtfs_import_service import GtfsImportService

# Імпортуємо функцію, яка повертає контейнер
from .fake_repos import FakeContainer, get_service


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


def _get_service_with_route() -> FakeContainer:
    container = get_service()

    agency = container.agency_repository.save(
        Agency(id=None, agency_id="metro", name="Kharkiv Metro", timezone="Europe/Kyiv")
    )
    assert agency.id is not None

    route = Route(
        id=None,
        agency_id=agency.id,
        route_id="11",
        short_name="11",
        long_name="Railway Station",
        route_type=3,
    )
    container.route_repository.save(route)

    return container


def test_import_trips_returns_imported_count() -> None:
    container = _get_service_with_route()

    rows = [
        {
            "route_id": "11",
            "trip_id": "T1",
            "trip_headsign": "Center",
        }
    ]

    imported = container.service.import_trips(rows)

    assert imported == 1


def test_import_trips_saves_valid_trip() -> None:
    container = get_service()

    agency = container.agency_repository.save(
        Agency(id=None, agency_id="metro", name="Kharkiv Metro", timezone="Europe/Kyiv")
    )

    assert agency.id is not None

    container.route_repository.save(
        Route(
            id=None,
            agency_id=agency.id,
            route_id="11",
            short_name="11",
            long_name="Station",
            route_type=3,
        )
    )

    rows = [
        {
            "route_id": "11",
            "trip_id": "T1",
            "trip_headsign": "Center",
        }
    ]

    container.service.import_trips(rows)

    assert len(container.trip_repository.saved) == 1
    trip = container.trip_repository.saved[0]

    assert trip.trip_id == "T1"
    assert trip.route_id == 1  # Перевіряємо, що зберігся внутрішній ID маршруту
    assert trip.headsign == "Center"


def test_import_trips_skips_unknown_route() -> None:
    container = _get_service_with_route()

    rows = [
        {
            "route_id": "999",  # Такого маршруту немає в БД
            "trip_id": "T1",
            "trip_headsign": "Center",
        }
    ]

    imported = container.service.import_trips(rows)

    assert imported == 0


def test_import_trips_skips_invalid_trip() -> None:
    container = get_service()
    agency = container.agency_repository.save(
        Agency(id=None, agency_id="metro", name="Kharkiv Metro", timezone="Europe/Kyiv")
    )
    assert agency.id is not None

    container.route_repository.save(
        Route(
            id=None,
            agency_id=agency.id,
            route_id="11",
            short_name="11",
            long_name="Station",
            route_type=3,
        )
    )

    rows = [
        {
            "route_id": "11",
            "trip_id": "",  # Невалідний рейс (немає trip_id)
            "trip_headsign": "Center",
        }
    ]

    imported = container.service.import_trips(rows)

    assert imported == 0
    assert len(container.trip_repository.saved) == 0


def test_import_trips_imports_only_valid_trips() -> None:
    container = _get_service_with_route()  # Тепер тут контейнер

    rows = [
        {"route_id": "11", "trip_id": "T1", "trip_headsign": "Valid"},
        {"route_id": "999", "trip_id": "T2", "trip_headsign": "Unknown Route"},
        {"route_id": "11", "trip_id": "", "trip_headsign": "Invalid"},
    ]

    imported = container.service.import_trips(rows)  # Звертаємось до service

    assert imported == 1
    assert len(container.trip_repository.saved) == 1
    assert container.trip_repository.saved[0].trip_id == "T1"


def _get_service_with_trip_and_stop() -> FakeContainer:
    container = get_service()

    agency = container.agency_repository.save(
        Agency(
            id=None,
            agency_id="metro",
            name="Kharkiv Metro",
            timezone="Europe/Kyiv",
        )
    )
    assert agency.id is not None

    route = container.route_repository.save(
        Route(
            id=None,
            agency_id=agency.id,
            route_id="11",
            short_name="11",
            long_name="Railway Station",
            route_type=3,
        )
    )
    assert route.id is not None

    trip = container.trip_repository.save(
        Trip(
            id=None,
            route_id=route.id,
            trip_id="trip_1",
            headsign="City Center",
        )
    )
    assert trip.id is not None

    stop = container.stop_repository.save(
        Stop(
            id=None,
            stop_id="stop_1",
            name="Central Station",
            latitude=49.9935,
            longitude=36.2304,
        )
    )
    assert stop.id is not None

    return container


def test_import_stop_times_returns_imported_count() -> None:
    container = _get_service_with_trip_and_stop()
    rows = [
        {
            "trip_id": "trip_1",
            "stop_id": "stop_1",
            "arrival_time": "08:00:00",
            "departure_time": "08:01:00",
            "stop_sequence": "1",
        }
    ]

    imported = container.service.import_stoptimes(rows)

    assert imported == 1


def test_import_stop_times_saves_valid_stop_time() -> None:
    container = _get_service_with_trip_and_stop()

    rows = [
        {
            "trip_id": "trip_1",
            "stop_id": "stop_1",
            "arrival_time": "08:00:00",
            "departure_time": "08:01:00",
            "stop_sequence": "1",
        }
    ]

    container.service.import_stoptimes(rows)

    assert len(container.stoptime_repository.saved) == 1


def test_import_stop_times_skips_unknown_trip() -> None:
    container = _get_service_with_trip_and_stop()

    rows = [
        {
            "trip_id": "unknown",
            "stop_id": "stop_1",
            "arrival_time": "08:00:00",
            "departure_time": "08:01:00",
            "stop_sequence": "1",
        }
    ]

    imported = container.service.import_stoptimes(rows)

    assert imported == 0
    assert len(container.stoptime_repository.saved) == 0


def test_import_stop_times_skips_unknown_stop() -> None:
    container = _get_service_with_trip_and_stop()

    rows = [
        {
            "trip_id": "trip_1",
            "stop_id": "unknown",
            "arrival_time": "08:00:00",
            "departure_time": "08:01:00",
            "stop_sequence": "1",
        }
    ]

    imported = container.service.import_stoptimes(rows)

    assert imported == 0
    assert len(container.stoptime_repository.saved) == 0


def test_import_stop_times_skips_invalid_row() -> None:
    container = _get_service_with_trip_and_stop()

    rows = [
        {
            "trip_id": "trip_1",
            "stop_id": "stop_1",
            "arrival_time": "",
            "departure_time": "08:01:00",
            "stop_sequence": "1",
        }
    ]

    imported = container.service.import_stoptimes(rows)

    assert imported == 0
    assert len(container.stoptime_repository.saved) == 0
