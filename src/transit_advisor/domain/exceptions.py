class DomainError(Exception):
    """Generic error class"""


class RouteNotFoundError(DomainError):
    def __init__(self, route_id: int) -> None:
        self.route_id = route_id
        super().__init__(f"Route {route_id} not found")


class AlreadySubscribedError(DomainError):
    def __init__(self, user_id: int, route_id: int) -> None:
        self.user_id = user_id
        self.route_id = route_id
        super().__init__(f"User {user_id} already subscribed to route {route_id}")


class SubscriptionNotFoundError(DomainError):
    def __init__(self, user_id: int, route_id: int) -> None:
        super().__init__(f"User {user_id} is not subscribed to route {route_id}")
        self.user_id = user_id
        self.route_id = route_id


class DuplicateScheduleVersionError(DomainError):
    def __init__(self, checksum: str) -> None:
        super().__init__(
            f"Schedule version with checksum {checksum[:8]}... already exists"
        )
        self.checksum = checksum
