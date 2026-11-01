from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UploadResult:
    imported: bool
    duplicate: bool
    checksum: str
