from typing import Protocol

from transit_advisor.domain.stop import Stop


class StopRepository(Protocol):
    def save(
        self,
        stop: Stop,
    ) -> Stop: ...

    def find_by_stop_id(
        self,
        stop_id: str,
    ) -> Stop | None: ...
