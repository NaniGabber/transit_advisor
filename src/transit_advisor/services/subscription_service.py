from transit_advisor.domain.subscription import Subscription
from transit_advisor.infrastructure.repositories.subscription import (
    SqlAlchemySubscriptionRepository,
)


class SubscriptionService:
    def __init__(
        self,
        repository: SqlAlchemySubscriptionRepository,
    ) -> None:
        self._repository = repository

    def subscribe(
        self,
        user_id: int,
        route_id: int,
    ) -> Subscription | None:
        existing = self._repository.find_by_user_and_route(
            user_id=user_id,
            route_id=route_id,
        )

        if existing is not None:
            return None

        return self._repository.save(
            Subscription(
                id=None,
                user_id=user_id,
                route_id=route_id,
            )
        )
