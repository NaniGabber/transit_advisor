from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ImportStats:
    imported: int
    rejected: int


@dataclass(frozen=True, slots=True)
class UploadResult:
    imported: bool
    duplicate: bool
    checksum: str
    stats: dict[str, ImportStats] = field(default_factory=dict)
