from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Notification:
    id: int | None

    subscription_id: int
    schedule_version_id: int

    message: str
    created_at: datetime

    is_read: bool = False

    def __post_init__(self) -> None:
        if self.subscription_id <= 0:
            raise ValueError("subscription_id must be positive")

        if self.schedule_version_id <= 0:
            raise ValueError("schedule_version_id must be positive")

        if not self.message.strip():
            raise ValueError("message cannot be empty")

        if len(self.message) > 1000:
            raise ValueError("message is too long")

    @property
    def is_unread(self) -> bool:
        return not self.is_read
