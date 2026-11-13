from transit_advisor.domain.exceptions import (
    AlreadySubscribedError,
    RouteNotFoundError,
    SubscriptionNotFoundError,
)
from transit_advisor.domain.repositories.route import RouteRepository
from transit_advisor.domain.repositories.subscription import SubscriptionRepository
from transit_advisor.domain.subscription import Subscription


class SubscriptionService:
    def __init__(
        self,
        repository: SubscriptionRepository,
        route_repository: RouteRepository,
    ) -> None:
        self._repository = repository
        self._route_repository = route_repository

    def subscribe(self, user_id: int, route_id: int) -> Subscription:
        """Підписати користувача на маршрут.

        ``route_id`` — внутрішній PK маршруту (``routes.id``), не GTFS route_id.
        """
        if self._route_repository.find_by_id(route_id) is None:
            raise RouteNotFoundError(route_id)

        if self._repository.find_by_user_and_route(user_id, route_id) is not None:
            raise AlreadySubscribedError(user_id, route_id)

        return self._repository.save(
            Subscription(id=None, user_id=user_id, route_id=route_id)
        )

    def unsubscribe(self, user_id: int, route_id: int) -> None:
        """Скасувати підписку. Кидає ``SubscriptionNotFoundError``, якщо немає."""
        subscription = self._repository.find_by_user_and_route(user_id, route_id)
        if subscription is None:
            raise SubscriptionNotFoundError(user_id, route_id)
        if subscription.id is None:
            raise RuntimeError("Subscription without id cannot be deleted")
        self._repository.delete(subscription.id)

    def list_for_user(self, user_id: int) -> list[Subscription]:
        return self._repository.find_by_user_id(user_id)
