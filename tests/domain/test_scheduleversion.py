from datetime import datetime

import pytest

from transit_advisor.domain.scheduleversion import ScheduleVersion


def test_create_valid_schedule_version() -> None:
    version = ScheduleVersion(
        id=None,
        checksum="a" * 64,
        imported_at=datetime.now(),
    )

    assert version.checksum == "a" * 64


@pytest.mark.parametrize(
    "checksum",
    [
        "",
        "abc",
        "12345",
    ],
)
def test_invalid_checksum_rejected(
    checksum: str,
) -> None:
    with pytest.raises(ValueError):
        ScheduleVersion(
            id=None,
            checksum=checksum,
            imported_at=datetime.now(),
        )
