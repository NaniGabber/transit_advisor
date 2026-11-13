from typing import Protocol

from transit_advisor.domain.agency import Agency


class AgencyRepository(Protocol):
    def save(
        self,
        agency: Agency,
    ) -> Agency: ...

    def save_all(
        self,
        agencies: list[Agency],
    ) -> list[Agency]: ...

    def find_by_agency_id(
        self,
        agency_id: str,
    ) -> Agency | None: ...

    def find_by_agency_ids(
        self,
        agency_ids: list[str],
    ) -> dict[str, Agency]: ...
