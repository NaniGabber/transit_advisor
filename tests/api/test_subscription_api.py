from transit_advisor.domain.route import Route
from transit_advisor.domain.subscription import Subscription
from transit_advisor.infrastructure.repositories.subscription import (
    SqlAlchemySubscriptionRepository,
)


def test_create_subscription(
    client,
    route: Route,
) -> None:
    assert route.id is not None

    response = client.post(
        "/subscriptions",
        json={
            "user_id": 1,
            "route_id": route.id,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == 1
    assert data["route_id"] == route.id


def test_duplicate_subscription_returns_409(
    client,
    route: Route,
) -> None:
    assert route.id is not None

    payload = {
        "user_id": 1,
        "route_id": route.id,
    }

    first = client.post(
        "/subscriptions",
        json=payload,
    )

    second = client.post(
        "/subscriptions",
        json=payload,
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_get_user_subscriptions(
    client,
    subscription_repository: SqlAlchemySubscriptionRepository,
    route: Route,
) -> None:
    assert route.id is not None

    subscription_repository.save(
        Subscription(
            id=None,
            user_id=1,
            route_id=route.id,
        )
    )

    response = client.get(
        "/subscriptions/users/1",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["user_id"] == 1
    assert data[0]["route_id"] == route.id


def test_get_empty_subscriptions(
    client,
) -> None:
    response = client.get(
        "/subscriptions/users/999",
    )

    assert response.status_code == 200
    assert response.json() == []


def test_create_subscription_with_invalid_payload(
    client,
) -> None:
    response = client.post(
        "/subscriptions",
        json={
            "user_id": 1,
        },
    )

    assert response.status_code == 422
