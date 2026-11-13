from collections.abc import Callable

import pytest

from transit_advisor.domain.exceptions import (
    AlreadySubscribedError,
    RouteNotFoundError,
)
from transit_advisor.domain.repositories.route import RouteRepository
from transit_advisor.domain.repositories.subscription import SubscriptionRepository
from transit_advisor.domain.route import Route
from transit_advisor.services.subscription_service import SubscriptionService


def test_subscribe_user(
    subscription_repository: SubscriptionRepository,
    route_repository: RouteRepository,
    route: Route,
) -> None:
    service = SubscriptionService(subscription_repository, route_repository)

    assert route.id is not None
    subscription = service.subscribe(user_id=1, route_id=route.id)

    assert subscription is not None
    assert subscription.user_id == 1
    assert subscription.route_id == route.id


def test_duplicate_subscription_rejected(
    subscription_repository: SubscriptionRepository,
    route_repository: RouteRepository,
    route: Route,
) -> None:
    service = SubscriptionService(subscription_repository, route_repository)
    assert route.id is not None
    service.subscribe(user_id=1, route_id=route.id)

    with pytest.raises(AlreadySubscribedError):
        service.subscribe(user_id=1, route_id=route.id)


def test_subscribe_unknown_route_raises(
    subscription_repository: SubscriptionRepository,
    route_repository: RouteRepository,
) -> None:
    service = SubscriptionService(subscription_repository, route_repository)

    with pytest.raises(RouteNotFoundError):
        service.subscribe(user_id=1, route_id=999)


def test_user_can_subscribe_to_multiple_routes(
    subscription_repository: SubscriptionRepository,
    route_repository: RouteRepository,
    route_factory: Callable[[str], Route],
) -> None:
    route1 = route_factory("11")
    route2 = route_factory("15")

    service = SubscriptionService(subscription_repository, route_repository)

    assert route1.id is not None
    first = service.subscribe(user_id=1, route_id=route1.id)

    assert route2.id is not None
    second = service.subscribe(user_id=1, route_id=route2.id)

    assert first is not None
    assert second is not None


def test_multiple_users_can_subscribe_to_same_route(
    subscription_repository: SubscriptionRepository,
    route_repository: RouteRepository,
    route: Route,
) -> None:
    service = SubscriptionService(subscription_repository, route_repository)
    assert route.id is not None

    first = service.subscribe(user_id=1, route_id=route.id)
    second = service.subscribe(user_id=2, route_id=route.id)

    assert first is not None
    assert second is not None
