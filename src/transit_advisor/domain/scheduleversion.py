import re
from dataclasses import dataclass
from datetime import datetime

_CHECKSUM_PATTERN = re.compile(r"[0-9a-f]{64}")


@dataclass(slots=True, frozen=True)
class ScheduleVersion:
    id: int | None
    checksum: str
    imported_at: datetime

    def __post_init__(self) -> None:
        if not _CHECKSUM_PATTERN.fullmatch(self.checksum):
            raise ValueError(
                "checksum must be a lowercase SHA-256 hex digest (64 chars)"
            )

    @property
    def short_checksum(self) -> str:
        return self.checksum[:8]
