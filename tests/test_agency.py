import pytest

from transit_advisor.domain.agency import Agency


@pytest.mark.parametrize(
    "agency_id, name, timezone",
    [
        ("", "Kharkiv Metro", "Europe/Kyiv"),
        ("metro", "", "Europe/Kyiv"),
        ("metro", "Kharkiv Metro", ""),
    ],
)
def test_invalid_agency_rejected(
    agency_id: str,
    name: str,
    timezone: str,
) -> None:
    with pytest.raises(ValueError):
        Agency(
            id=None,
            agency_id=agency_id,
            name=name,
            timezone=timezone,
        )


def test_create_valid_agency() -> None:
    agency = Agency(
        id=None,
        agency_id="metro",
        name="Kharkiv Metro",
        timezone="Europe/Kyiv",
    )

    assert agency.agency_id == "metro"
    assert agency.name == "Kharkiv Metro"
