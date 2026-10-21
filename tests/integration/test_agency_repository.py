from transit_advisor.domain.agency import Agency
from transit_advisor.infrastructure.repositories.agency import (
    SqlAlchemyAgencyRepository,
)


def test_save_agency(agency_repository: SqlAlchemyAgencyRepository) -> None: ...


def test_find_by_agency_id(
    agency_repository: SqlAlchemyAgencyRepository,
) -> None:
    agency = Agency(
        id=None,
        agency_id="metro",
        name="Kharkiv Metro",
        timezone="Europe/Kyiv",
    )

    agency_repository.save(
        agency,
    )

    found = agency_repository.find_by_agency_id(
        "metro",
    )

    assert found is not None
    assert found.agency_id == "metro"
    assert found.name == "Kharkiv Metro"


def test_find_by_agency_id_returns_none_for_missing_agency(
    agency_repository: SqlAlchemyAgencyRepository,
) -> None:
    found = agency_repository.find_by_agency_id(
        "missing",
    )

    assert found is None
