from transit_advisor.domain.agency import Agency
from transit_advisor.infrastructure.gtfs.parsing import normalize


def to_agency(row: dict[str, str]) -> Agency | None:
    agency_id = row.get("agency_id", "").strip()
    name = row.get("agency_name", "").strip()
    timezone = row.get("agency_timezone", "").strip()

    try:
        return Agency(
            id=None,
            agency_id=agency_id,
            name=normalize(name),
            timezone=timezone,
            language=row.get("agency_lang"),
            phone=row.get("agency_phone"),
            fare_url=row.get("agency_fare_url"),
            email=row.get("agency_email"),
        )
    except ValueError:
        return None
