from dataclasses import dataclass


@dataclass(slots=True)
class Subscription:
    id: int | None

    user_id: int
    route_id: str

    is_active: bool = True

    def __post_init__(self) -> None:
        if self.user_id <= 0:
            raise ValueError("user_id must be positive")

        if self.route_id is None:
            raise ValueError("route_id cannot be empty")

    @property
    def is_inactive(self) -> bool:
        return not self.is_active
