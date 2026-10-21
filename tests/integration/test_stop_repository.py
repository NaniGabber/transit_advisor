from transit_advisor.domain.stop import Stop
from transit_advisor.infrastructure.repositories.stop import (
    SqlAlchemyStopRepository,
)


def test_save_stop(
    stop_repository: SqlAlchemyStopRepository,
) -> None:
    stop = Stop(
        id=None,
        stop_id="stop_1",
        name="Central Station",
        latitude=49.9935,
        longitude=36.2304,
    )

    saved = stop_repository.save(stop)

    assert saved.id is not None
    assert saved.stop_id == "stop_1"


def test_find_by_stop_id(
    stop_repository: SqlAlchemyStopRepository,
) -> None:
    stop = Stop(
        id=None,
        stop_id="stop_1",
        name="Central Station",
        latitude=49.9935,
        longitude=36.2304,
    )

    stop_repository.save(stop)

    found = stop_repository.find_by_stop_id(
        "stop_1",
    )

    assert found is not None


def test_find_by_stop_id_returns_none_for_missing_stop(
    stop_repository: SqlAlchemyStopRepository,
) -> None:
    found = stop_repository.find_by_stop_id(
        "missing",
    )

    assert found is None


def test_saved_stop_can_be_loaded(
    stop_repository: SqlAlchemyStopRepository,
) -> None:
    stop = Stop(
        id=None,
        stop_id="stop_1",
        name="Central Station",
        latitude=49.9935,
        longitude=36.2304,
    )

    saved = stop_repository.save(stop)

    loaded = stop_repository.find_by_stop_id(
        saved.stop_id,
    )

    assert loaded is not None
    assert loaded.stop_id == saved.stop_id
    assert loaded.latitude == saved.latitude
    assert loaded.longitude == saved.longitude
