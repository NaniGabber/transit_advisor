from dataclasses import dataclass


@dataclass(slots=True)
class Agency:
    id: int | None

    agency_id: str
    name: str
    timezone: str

    language: str | None = None
    phone: str | None = None
    fare_url: str | None = None
    email: str | None = None

    def __post_init__(self) -> None:
        if not self.agency_id.strip():
            raise ValueError("agency_id cannot be empty")

        if not self.name.strip():
            raise ValueError("agency name cannot be empty")

        if not self.timezone.strip():
            raise ValueError("timezone cannot be empty")

        if len(self.agency_id) > 100:
            raise ValueError("agency_id is too long")

        if len(self.name) > 255:
            raise ValueError("agency name is too long")
