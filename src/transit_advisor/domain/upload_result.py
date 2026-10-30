from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UploadResult:
    imported: bool
    duplicate: bool
    checksum: str

    def __post_init__(self) -> None:
        if self.imported == self.duplicate:
            raise ValueError("exactly one of imported/duplicate must be True")
