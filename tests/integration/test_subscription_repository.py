from transit_advisor.domain.agency import Agency
from transit_advisor.domain.route import Route
from transit_advisor.domain.subscription import (
    Subscription,
)
from transit_advisor.infrastructure.repositories.route import (
    SqlAlchemyRouteRepository,
)
from transit_advisor.infrastructure.repositories.subscription import (
    SqlAlchemySubscriptionRepository,
)


def test_save_subscription(
    subscription_repository: SqlAlchemySubscriptionRepository,
    route_repository: SqlAlchemyRouteRepository,
    agency: Agency,
) -> None:
    if agency.id is None:
        return

    route = route_repository.save(_make_route(agency.id, "11"))
    assert route.id is not None

    subscription = Subscription(
        id=None,
        user_id=1,
        route_id=route.id,
    )

    saved = subscription_repository.save(
        subscription,
    )

    assert saved.id is not None
    assert saved.user_id == 1
    assert saved.route_id == route.id


def test_find_by_user_id(
    subscription_repository: SqlAlchemySubscriptionRepository,
    route_repository: SqlAlchemyRouteRepository,
    agency: Agency,
) -> None:
    if agency.id is None:
        return

    route = route_repository.save(_make_route(agency.id, "11"))
    assert route.id is not None

    subscription_repository.save(
        Subscription(
            id=None,
            user_id=1,
            route_id=route.id,
        )
    )

    subscriptions = subscription_repository.find_by_user_id(
        1,
    )

    assert len(subscriptions) == 1
    assert subscriptions[0].user_id == 1


def test_find_by_route_id(
    subscription_repository: SqlAlchemySubscriptionRepository,
    route_repository: SqlAlchemyRouteRepository,
    agency: Agency,
) -> None:
    if agency.id is None:
        return

    route = route_repository.save(_make_route(agency.id, "5"))
    assert route.id is not None
    subscription_repository.save(
        Subscription(
            id=None,
            user_id=1,
            route_id=route.id,
        )
    )

    subscriptions = subscription_repository.find_by_route_id(
        route.id,
    )

    assert len(subscriptions) == 1
    assert subscriptions[0].route_id == route.id


def test_find_by_user_and_route(
    subscription_repository: SqlAlchemySubscriptionRepository,
    route_repository: SqlAlchemyRouteRepository,
    agency: Agency,
) -> None:
    if agency.id is None:
        return

    route = route_repository.save(_make_route(agency.id, "5"))
    assert route.id is not None
    subscription_repository.save(
        Subscription(
            id=None,
            user_id=1,
            route_id=route.id,
        )
    )

    subscription = subscription_repository.find_by_user_and_route(
        user_id=1,
        route_id=route.id,
    )

    assert subscription is not None
    assert subscription.user_id == 1
    assert subscription.route_id == route.id


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
        route_id=1,
    )

    assert subscription is None


def _make_route(agency_id: int, route_id: str) -> Route:
    from transit_advisor.domain.route import Route

    return Route(
        id=None,
        agency_id=agency_id,
        route_id=route_id,
        short_name=route_id,
        long_name=f"Route {route_id}",
        route_type=3,
    )
