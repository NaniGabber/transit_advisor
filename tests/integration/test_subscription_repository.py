from transit_advisor.domain.route import Route
from transit_advisor.domain.subscription import (
    Subscription,
)
from transit_advisor.infrastructure.repositories.subscription import (
    SqlAlchemySubscriptionRepository,
)


def test_save_subscription(
    subscription_repository: SqlAlchemySubscriptionRepository,
    route: Route,
) -> None:
    subscription = Subscription(
        id=None,
        user_id=1,
        route_id=route.route_id,
    )

    saved = subscription_repository.save(
        subscription,
    )

    assert saved.id is not None
    assert saved.user_id == 1
    assert saved.route_id == route.route_id


def test_find_by_user_id(
    subscription_repository: SqlAlchemySubscriptionRepository,
    route: Route,
) -> None:
    subscription_repository.save(
        Subscription(
            id=None,
            user_id=1,
            route_id=route.route_id,
        )
    )

    subscriptions = subscription_repository.find_by_user_id(
        1,
    )

    assert len(subscriptions) == 1
    assert subscriptions[0].user_id == 1


def test_find_by_route_id(
    subscription_repository: SqlAlchemySubscriptionRepository,
    route: Route,
) -> None:
    subscription_repository.save(
        Subscription(
            id=None,
            user_id=1,
            route_id=route.route_id,
        )
    )

    subscriptions = subscription_repository.find_by_route_id(
        route.route_id,
    )

    assert len(subscriptions) == 1
    assert subscriptions[0].route_id == route.route_id


def test_find_by_user_and_route(
    subscription_repository: SqlAlchemySubscriptionRepository,
    route: Route,
) -> None:
    subscription_repository.save(
        Subscription(
            id=None,
            user_id=1,
            route_id=route.route_id,
        )
    )

    subscription = subscription_repository.find_by_user_and_route(
        user_id=1,
        route_id=route.route_id,
    )

    assert subscription is not None
    assert subscription.user_id == 1
    assert subscription.route_id == route.route_id


def test_find_by_user_id_returns_empty_list(
    subscription_repository: SqlAlchemySubscriptionRepository,
) -> None:
    subscriptions = subscription_repository.find_by_user_id(
        999,
    )

    assert subscriptions == []


def test_find_by_user_and_route_returns_none(
    subscription_repository: SqlAlchemySubscriptionRepository,
) -> None:
    subscription = subscription_repository.find_by_user_and_route(
        user_id=1,
        route_id="11",
    )

    assert subscription is None
