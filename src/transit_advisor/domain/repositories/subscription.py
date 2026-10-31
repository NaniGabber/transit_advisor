from typing import Protocol

from transit_advisor.domain.subscription import Subscription


class SubscriptionRepository(Protocol):
    def save(
        self,
        subscription: Subscription,
    ) -> Subscription: ...

    def find_by_user_id(
        self,
        user_id: int,
    ) -> list[Subscription]: ...

    def find_by_route_id(
        self,
        route_id: int,
    ) -> list[Subscription]: ...
