from dataclasses import dataclass


@dataclass(slots=True)
class ScheduleDiff:
    added_routes: list[str]
    removed_routes: list[str]

    def __post_init__(self) -> None:
        if any(not route_id.strip() for route_id in self.added_routes):
            raise ValueError(
                "added_routes contains empty route id",
            )

        if any(not route_id.strip() for route_id in self.removed_routes):
            raise ValueError(
                "removed_routes contains empty route id",
            )

        if set(self.added_routes) & set(self.removed_routes):
            raise ValueError(
                "route cannot be both added and removed",
            )
