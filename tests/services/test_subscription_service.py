from collections.abc import Callable

import pytest

from transit_advisor.domain.exceptions import (
    AlreadySubscribedError,
    RouteNotFoundError,
    SubscriptionNotFoundError,
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


# ---------- unsubscribe ----------


def test_unsubscribe_removes_subscription(
    subscription_repository: SubscriptionRepository,
    route_repository: RouteRepository,
    route: Route,
) -> None:
    service = SubscriptionService(subscription_repository, route_repository)
    assert route.id is not None

    subscription = service.subscribe(user_id=1, route_id=route.id)
    assert subscription.id is not None

    service.unsubscribe(user_id=1, route_id=route.id)

    remaining = subscription_repository.find_by_user_id(1)
    assert remaining == []


def test_unsubscribe_unknown_subscription_raises(
    subscription_repository: SubscriptionRepository,
    route_repository: RouteRepository,
    route: Route,
) -> None:
    service = SubscriptionService(subscription_repository, route_repository)
    assert route.id is not None

    with pytest.raises(SubscriptionNotFoundError):
        service.unsubscribe(user_id=1, route_id=route.id)


def test_unsubscribe_does_not_affect_other_users(
    subscription_repository: SubscriptionRepository,
    route_repository: RouteRepository,
    route: Route,
) -> None:
    service = SubscriptionService(subscription_repository, route_repository)
    assert route.id is not None

    service.subscribe(user_id=1, route_id=route.id)
    service.subscribe(user_id=2, route_id=route.id)

    service.unsubscribe(user_id=1, route_id=route.id)

    user1_subs = subscription_repository.find_by_user_id(1)
    user2_subs = subscription_repository.find_by_user_id(2)

    assert user1_subs == []
    assert len(user2_subs) == 1
    assert user2_subs[0].user_id == 2


def test_unsubscribe_does_not_affect_other_routes(
    subscription_repository: SubscriptionRepository,
    route_repository: RouteRepository,
    route_factory: Callable[[str], Route],
) -> None:
    route1 = route_factory("11")
    route2 = route_factory("15")

    service = SubscriptionService(subscription_repository, route_repository)

    assert route1.id is not None
    assert route2.id is not None

    service.subscribe(user_id=1, route_id=route1.id)
    service.subscribe(user_id=1, route_id=route2.id)

    service.unsubscribe(user_id=1, route_id=route1.id)

    remaining = subscription_repository.find_by_user_id(1)
    assert len(remaining) == 1
    assert remaining[0].route_id == route2.id


# ---------- list_for_user ----------


def test_list_for_user_returns_empty_when_no_subscriptions(
    subscription_repository: SubscriptionRepository,
    route_repository: RouteRepository,
) -> None:
    service = SubscriptionService(subscription_repository, route_repository)

    assert service.list_for_user(user_id=42) == []


def test_list_for_user_returns_only_own_subscriptions(
    subscription_repository: SubscriptionRepository,
    route_repository: RouteRepository,
    route_factory: Callable[[str], Route],
) -> None:
    route1 = route_factory("11")
    route2 = route_factory("15")

    service = SubscriptionService(subscription_repository, route_repository)

    assert route1.id is not None
    assert route2.id is not None

    service.subscribe(user_id=1, route_id=route1.id)
    service.subscribe(user_id=1, route_id=route2.id)
    service.subscribe(user_id=2, route_id=route1.id)

    user1_subs = service.list_for_user(user_id=1)
    user2_subs = service.list_for_user(user_id=2)

    assert len(user1_subs) == 2
    assert len(user2_subs) == 1
    assert {s.route_id for s in user1_subs} == {route1.id, route2.id}
    assert user2_subs[0].route_id == route1.id


def test_list_for_user_after_unsubscribe(
    subscription_repository: SubscriptionRepository,
    route_repository: RouteRepository,
    route: Route,
) -> None:
    service = SubscriptionService(subscription_repository, route_repository)
    assert route.id is not None

    service.subscribe(user_id=1, route_id=route.id)
    service.unsubscribe(user_id=1, route_id=route.id)

    assert service.list_for_user(user_id=1) == []
