from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ScheduleVersion:
    id: int | None

    checksum: str
    imported_at: datetime

    def __post_init__(self) -> None:
        if not self.checksum.strip():
            raise ValueError("checksum cannot be empty")

        if len(self.checksum) != 64:
            raise ValueError("checksum must be a SHA-256 hash")

    @property
    def short_checksum(self) -> str:
        return self.checksum[:8]
