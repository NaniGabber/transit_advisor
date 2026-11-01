from transit_advisor.domain.route import Route
from transit_advisor.infrastructure.repositories.subscription import (
    SqlAlchemySubscriptionRepository,
)
from transit_advisor.services.subscription_service import (
    SubscriptionService,
)


def test_subscribe_user(
    subscription_repository: SqlAlchemySubscriptionRepository,
    route: Route,
) -> None:
    service = SubscriptionService(
        subscription_repository,
    )

    assert route.id is not None
    subscription = service.subscribe(
        user_id=1,
        route_id=route.id,
    )

    assert subscription is not None
    assert subscription.user_id == 1
    assert subscription.route_id == route.id


def test_duplicate_subscription_rejected(
    subscription_repository: SqlAlchemySubscriptionRepository,
    route: Route,
) -> None:
    service = SubscriptionService(
        subscription_repository,
    )
    assert route.id is not None
    service.subscribe(
        user_id=1,
        route_id=route.id,
    )

    subscription = service.subscribe(
        user_id=1,
        route_id=route.id,
    )

    assert subscription is None


def test_user_can_subscribe_to_multiple_routes(
    subscription_repository: SqlAlchemySubscriptionRepository,
    route_factory,
) -> None:
    route1 = route_factory("11")
    route2 = route_factory("15")

    service = SubscriptionService(
        subscription_repository,
    )

    first = service.subscribe(
        user_id=1,
        route_id=route1.id,
    )

    second = service.subscribe(
        user_id=1,
        route_id=route2.id,
    )

    assert first is not None
    assert second is not None


def test_multiple_users_can_subscribe_to_same_route(
    subscription_repository: SqlAlchemySubscriptionRepository,
    route: Route,
) -> None:
    service = SubscriptionService(
        subscription_repository,
    )
    assert route.id is not None
    first = service.subscribe(
        user_id=1,
        route_id=route.id,
    )

    second = service.subscribe(
        user_id=2,
        route_id=route.id,
    )

    assert first is not None
    assert second is not None
