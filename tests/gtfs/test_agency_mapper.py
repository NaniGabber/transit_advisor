import pytest

from transit_advisor.infrastructure.gtfs.mappers.agency import (
    to_agency,
)


def test_to_agency_returns_agency_for_valid_row() -> None:
    row = {
        "agency_id": "metro",
        "agency_name": "Kharkiv Metro",
        "agency_timezone": "Europe/Kyiv",
    }

    agency = to_agency(row)

    assert agency is not None
    assert agency.agency_id == "metro"
    assert agency.name == "Kharkiv Metro"
    assert agency.timezone == "Europe/Kyiv"


@pytest.mark.parametrize(
    "row",
    [
        {
            "agency_id": "",
            "agency_name": "Kharkiv Metro",
            "agency_timezone": "Europe/Kyiv",
        },
        {
            "agency_id": "metro",
            "agency_name": "",
            "agency_timezone": "Europe/Kyiv",
        },
        {
            "agency_id": "metro",
            "agency_name": "Kharkiv Metro",
            "agency_timezone": "",
        },
    ],
)
def test_to_agency_returns_none_for_invalid_row(
    row: dict[str, str],
) -> None:
    assert to_agency(row) is None
