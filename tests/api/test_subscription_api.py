import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from transit_advisor.api import dependencies
from transit_advisor.domain.route import Route
from transit_advisor.domain.subscription import Subscription
from transit_advisor.infrastructure.repositories.subscription import (
    SqlAlchemySubscriptionRepository,
)


def test_create_subscription(client: TestClient, route: Route) -> None:
    assert route.id is not None

    response = client.post(
        "/api/v1/subscriptions",
        headers={"X-Role": "user"},
        json={"user_id": 1, "route_id": route.id},
    )
    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == 1
    assert data["route_id"] == route.id


def test_get_session_commits_subscription(
    session: Session,
    session_factory: sessionmaker[Session],
    route: Route,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert route.id is not None
    session.commit()
    monkeypatch.setattr(dependencies, "SessionLocal", session_factory)

    request_session_generator = dependencies.get_session()
    request_session = next(request_session_generator)
    saved = SqlAlchemySubscriptionRepository(request_session).save(
        Subscription(id=None, user_id=1, route_id=route.id)
    )
    assert saved.id is not None

    with pytest.raises(StopIteration):
        next(request_session_generator)

    with session_factory() as verification_session:
        persisted = SqlAlchemySubscriptionRepository(
            verification_session,
        ).find_by_id(saved.id)

    assert persisted is not None


def test_duplicate_subscription_returns_409(
    client: TestClient,
    route: Route,
) -> None:
    assert route.id is not None

    payload = {
        "user_id": 10001,
        "route_id": route.id,
    }

    first = client.post(
        "/api/v1/subscriptions",
        headers={"X-Role": "user"},
        json=payload,
    )

    duplicate_responses = [
        client.post(
            "/api/v1/subscriptions",
            headers={"X-Role": "user"},
            json=payload,
        )
        for _ in range(3)
    ]

    assert first.status_code == 201
    assert [response.status_code for response in duplicate_responses] == [
        409,
        409,
        409,
    ]

    subscriptions = client.get("/api/v1/subscriptions/users/10001")
    assert subscriptions.status_code == 200
    assert len(subscriptions.json()) == 1


def test_get_user_subscriptions(
    client: TestClient,
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
        "/api/v1/subscriptions",
        params={"user_id": 1},
        headers={"X-Role": "user"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["user_id"] == 1
    assert data[0]["route_id"] == route.id


def test_get_empty_subscriptions(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/subscriptions/users/999",
    )

    assert response.status_code == 200
    assert response.json() == []


def test_create_subscription_with_invalid_payload(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/subscriptions",
        headers={"X-Role": "user"},
        json={
            "user_id": 1,
        },
    )

    assert response.status_code == 422
