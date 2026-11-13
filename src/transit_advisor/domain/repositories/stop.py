from typing import Protocol

from transit_advisor.domain.stop import Stop


class StopRepository(Protocol):
    def save(
        self,
        stop: Stop,
    ) -> Stop: ...

    def save_all(
        self,
        stops: list[Stop],
    ) -> list[Stop]: ...

    def find_by_stop_id(
        self,
        stop_id: str,
    ) -> Stop | None: ...

    def find_by_stop_ids(
        self,
        stop_ids: list[str],
    ) -> dict[str, Stop]: ...
