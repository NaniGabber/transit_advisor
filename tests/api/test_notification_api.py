from datetime import UTC, datetime

from fastapi.testclient import TestClient

from tests.services.fake_repos import FakeNotificationRepository
from transit_advisor.domain.notification import Notification


def _make_notification(
    notification_id: int,
    user_id: int,
    is_read: bool,
) -> Notification:
    return Notification(
        id=notification_id,
        user_id=user_id,
        subscription_id=1,
        schedule_version_id=1,
        message=f"Notification {notification_id}",
        created_at=datetime(2026, 11, 1, 12, 0, tzinfo=UTC),
        is_read=is_read,
    )


def test_get_notifications(
    client: TestClient,
    notification_repository: FakeNotificationRepository,
) -> None:
    notification_repository.saved.extend(
        [
            _make_notification(1, user_id=42, is_read=False),
            _make_notification(2, user_id=42, is_read=True),
            _make_notification(3, user_id=99, is_read=False),
        ]
    )

    response = client.get("/notifications/users/42")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {item["id"] for item in data} == {1, 2}
    assert all(item["user_id"] == 42 for item in data)


def test_get_unread_notifications(
    client: TestClient,
    notification_repository: FakeNotificationRepository,
) -> None:
    notification_repository.saved.extend(
        [
            _make_notification(1, user_id=42, is_read=False),
            _make_notification(2, user_id=42, is_read=True),
            _make_notification(3, user_id=42, is_read=False),
        ]
    )

    response = client.get("/notifications/users/42/unread")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {item["id"] for item in data} == {1, 3}
    assert all(item["is_read"] is False for item in data)


def test_returns_empty_list_for_unknown_user(
    client: TestClient,
    notification_repository: FakeNotificationRepository,
) -> None:
    notification_repository.saved.append(
        _make_notification(1, user_id=42, is_read=False)
    )

    response = client.get("/notifications/users/999")

    assert response.status_code == 200
    assert response.json() == []
