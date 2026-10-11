import pytest

from transit_advisor.domain.agency import Agency


def test_create_agency() -> None:
    agency = Agency(
        id=None,
        agency_id="metro",
        name="Kharkiv Metro",
        timezone="Europe/Kyiv",
    )

    assert agency.name == "Kharkiv Metro"


def test_empty_name_raises_error() -> None:
    with pytest.raises(ValueError):
        Agency(
            id=None,
            agency_id="metro",
            name="",
            timezone="Europe/Kyiv",
        )
