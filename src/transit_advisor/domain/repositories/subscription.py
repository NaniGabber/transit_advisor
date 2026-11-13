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

    def find_by_user_and_route(
        self,
        user_id: int,
        route_id: int,
    ) -> Subscription | None: ...

    def delete(self, subscription_id: int) -> None: ...
