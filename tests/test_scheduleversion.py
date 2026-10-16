from datetime import datetime

import pytest

from transit_advisor.domain.scheduleversion import ScheduleVersion


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
