from datetime import datetime

import pytest

from transit_advisor.domain.notification import Notification


@pytest.mark.parametrize(
    "subscription_id, schedule_version_id, message",
    [
        (0, 1, "changed"),
        (1, 0, "changed"),
        (1, 1, ""),
    ],
)
def test_invalid_notification_rejected(
    subscription_id: int,
    schedule_version_id: int,
    message: str,
) -> None:
    with pytest.raises(ValueError):
        Notification(
            id=None,
            subscription_id=subscription_id,
            schedule_version_id=schedule_version_id,
            message=message,
            created_at=datetime.now(),
        )
