from typing import Protocol

from transit_advisor.domain.agency import Agency


class AgencyRepository(Protocol):
    def save(
        self,
        agency: Agency,
    ) -> Agency: ...

    def find_by_agency_id(
        self,
        agency_id: str,
    ) -> Agency | None: ...
