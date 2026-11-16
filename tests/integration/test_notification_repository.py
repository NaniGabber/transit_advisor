import hashlib
from datetime import UTC, datetime, timedelta

from transit_advisor.domain.agency import Agency
from transit_advisor.domain.notification import Notification
from transit_advisor.domain.route import Route
from transit_advisor.domain.scheduleversion import ScheduleVersion
from transit_advisor.domain.subscription import Subscription
from transit_advisor.infrastructure.repositories.notification import (
    SqlAlchemyNotificationRepository,
)
from transit_advisor.infrastructure.repositories.route import (
    SqlAlchemyRouteRepository,
)
from transit_advisor.infrastructure.repositories.scheduleversion import (
    SqlAlchemyScheduleVersionRepository,
)
from transit_advisor.infrastructure.repositories.subscription import (
    SqlAlchemySubscriptionRepository,
)

# ---------- helpers ----------


def _make_route(agency_id: int, route_id: str) -> Route:
    return Route(
        id=None,
        agency_id=agency_id,
        route_id=route_id,
        short_name=route_id,
        long_name=f"Route {route_id}",
        route_type=3,
    )


def _make_subscription(user_id: int, route_id: int) -> Subscription:
    return Subscription(
        id=None,
        user_id=user_id,
        route_id=route_id,
    )


def _make_notification(
    user_id: int,
    subscription_id: int,
    schedule_version_id: int,
    message: str,
    is_read: bool = False,
    created_at: datetime | None = None,
) -> Notification:
    return Notification(
        id=None,
        user_id=user_id,
        subscription_id=subscription_id,
        schedule_version_id=schedule_version_id,
        message=message,
        created_at=created_at or datetime.now(UTC),
        is_read=is_read,
    )


def _make_version(
    repository: SqlAlchemyScheduleVersionRepository,
    seed: str,
) -> ScheduleVersion:
    """Створює унікальну версію (checksum = sha256(seed)).

    Потрібно, бо `uq_notification (subscription_id, schedule_version_id)`
    забороняє кілька сповіщень з однаковою парою.
    """
    checksum = hashlib.sha256(seed.encode()).hexdigest()
    return repository.save(
        ScheduleVersion(
            id=None,
            checksum=checksum,
            imported_at=datetime.now(),
        )
    )


# ---------- save ----------


def test_save_notification(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    saved = notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Route 15 was added",
        )
    )

    assert saved.id is not None
    assert saved.user_id == 1
    assert saved.subscription_id == subscription_id
    assert saved.schedule_version_id == version_id
    assert saved.message == "Route 15 was added"
    assert saved.is_read is False
    assert isinstance(saved.created_at, datetime)


def test_save_assigns_distinct_ids(
    notification_repository: SqlAlchemyNotificationRepository,
    route_repository: SqlAlchemyRouteRepository,
    subscription_repository: SqlAlchemySubscriptionRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    agency: Agency,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id_1, _ = notification_parents
    assert agency.id is not None

    route_2 = route_repository.save(_make_route(agency.id, "12"))
    assert route_2.id is not None
    subscription_2 = subscription_repository.save(_make_subscription(1, route_2.id))
    assert subscription_2.id is not None

    v1 = _make_version(schedule_version_repository, "save-distinct-1")
    v2 = _make_version(schedule_version_repository, "save-distinct-2")
    assert v1.id is not None
    assert v2.id is not None

    first = notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id_1,
            schedule_version_id=v1.id,
            message="First",
        )
    )
    second = notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_2.id,
            schedule_version_id=v2.id,
            message="Second",
        )
    )

    assert first.id is not None
    assert second.id is not None
    assert first.id != second.id


def test_save_persists_is_read_true(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    saved = notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Read notification",
            is_read=True,
        )
    )

    assert saved.is_read is True


def test_save_persists_is_read_false(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    saved = notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Unread",
            is_read=False,
        )
    )

    assert saved.is_read is False


def test_save_persists_created_at(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents
    created_at = datetime(2026, 1, 1, 12, 0)

    saved = notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="x",
            created_at=created_at,
        )
    )

    assert saved.created_at == created_at


# ---------- save_all ----------


def test_save_all_persists_all_notifications(
    notification_repository: SqlAlchemyNotificationRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, _ = notification_parents

    versions = [
        _make_version(schedule_version_repository, f"save-all-{i}") for i in range(3)
    ]
    for v in versions:
        assert v.id is not None

    saved = notification_repository.save_all(
        [
            _make_notification(
                user_id=1,
                subscription_id=subscription_id,
                schedule_version_id=v.id or 0,
                message=f"msg {i}",
            )
            for i, v in enumerate(versions)
        ]
    )

    assert len(saved) == 3
    assert all(n.id is not None for n in saved)
    assert len({n.id for n in saved}) == 3
    assert len(notification_repository.find_by_user_id(1)) == 3


def test_save_all_returns_empty_for_empty_input(
    notification_repository: SqlAlchemyNotificationRepository,
) -> None:
    assert notification_repository.save_all([]) == []


def test_save_all_assigns_distinct_ids(
    notification_repository: SqlAlchemyNotificationRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, _ = notification_parents

    v1 = _make_version(schedule_version_repository, "save-all-distinct-1")
    v2 = _make_version(schedule_version_repository, "save-all-distinct-2")
    assert v1.id is not None
    assert v2.id is not None

    saved = notification_repository.save_all(
        [
            _make_notification(
                user_id=1,
                subscription_id=subscription_id,
                schedule_version_id=v1.id,
                message="a",
            ),
            _make_notification(
                user_id=1,
                subscription_id=subscription_id,
                schedule_version_id=v2.id,
                message="b",
            ),
        ]
    )

    assert saved[0].id != saved[1].id


# ---------- find_by_user_id ----------


def test_find_by_user_id(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Route 15 was added",
        )
    )

    notifications = notification_repository.find_by_user_id(1)

    assert len(notifications) == 1
    assert notifications[0].user_id == 1
    assert notifications[0].message == "Route 15 was added"


def test_find_by_user_id_returns_all_for_user(
    notification_repository: SqlAlchemyNotificationRepository,
    route_repository: SqlAlchemyRouteRepository,
    subscription_repository: SqlAlchemySubscriptionRepository,
    agency: Agency,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id_1, version_id = notification_parents
    assert agency.id is not None

    route_2 = route_repository.save(_make_route(agency.id, "12"))
    assert route_2.id is not None
    subscription_2 = subscription_repository.save(_make_subscription(1, route_2.id))
    assert subscription_2.id is not None

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id_1,
            schedule_version_id=version_id,
            message="First",
        )
    )
    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_2.id,
            schedule_version_id=version_id,
            message="Second",
        )
    )

    notifications = notification_repository.find_by_user_id(1)

    assert len(notifications) == 2
    assert {n.message for n in notifications} == {"First", "Second"}


def test_find_by_user_id_does_not_leak_other_users(
    notification_repository: SqlAlchemyNotificationRepository,
    route_repository: SqlAlchemyRouteRepository,
    subscription_repository: SqlAlchemySubscriptionRepository,
    agency: Agency,
    notification_parents: tuple[int, int],
) -> None:
    _, version_id = notification_parents
    assert agency.id is not None

    route_1 = route_repository.save(_make_route(agency.id, "100"))
    route_2 = route_repository.save(_make_route(agency.id, "101"))
    assert route_1.id is not None
    assert route_2.id is not None

    sub_1 = subscription_repository.save(_make_subscription(1, route_1.id))
    sub_2 = subscription_repository.save(_make_subscription(2, route_2.id))
    assert sub_1.id is not None
    assert sub_2.id is not None

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=sub_1.id,
            schedule_version_id=version_id,
            message="For user 1",
        )
    )
    notification_repository.save(
        _make_notification(
            user_id=2,
            subscription_id=sub_2.id,
            schedule_version_id=version_id,
            message="For user 2",
        )
    )

    notifications = notification_repository.find_by_user_id(1)

    assert len(notifications) == 1
    assert notifications[0].message == "For user 1"


def test_find_by_user_id_returns_empty_list(
    notification_repository: SqlAlchemyNotificationRepository,
) -> None:
    assert notification_repository.find_by_user_id(999) == []


def test_find_by_user_id_returns_newest_first(
    notification_repository: SqlAlchemyNotificationRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, _ = notification_parents
    base = datetime.now()

    v_old = _make_version(schedule_version_repository, "order-old")
    v_mid = _make_version(schedule_version_repository, "order-mid")
    v_new = _make_version(schedule_version_repository, "order-new")
    assert v_old.id is not None
    assert v_mid.id is not None
    assert v_new.id is not None

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=v_old.id,
            message="old",
            created_at=base - timedelta(hours=2),
        )
    )
    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=v_mid.id,
            message="mid",
            created_at=base - timedelta(hours=1),
        )
    )
    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=v_new.id,
            message="new",
            created_at=base,
        )
    )

    result = notification_repository.find_by_user_id(1)

    assert [n.message for n in result] == ["new", "mid", "old"]


def test_find_by_user_id_applies_pagination(
    notification_repository: SqlAlchemyNotificationRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, _ = notification_parents

    for i in range(5):
        version = _make_version(schedule_version_repository, f"pagination-{i}")
        assert version.id is not None
        notification_repository.save(
            _make_notification(
                user_id=1,
                subscription_id=subscription_id,
                schedule_version_id=version.id,
                message=f"msg {i}",
            )
        )

    page1 = notification_repository.find_by_user_id(1, offset=0, limit=2)
    page2 = notification_repository.find_by_user_id(1, offset=2, limit=2)
    page3 = notification_repository.find_by_user_id(1, offset=4, limit=2)

    assert len(page1) == 2
    assert len(page2) == 2
    assert len(page3) == 1

    ids1 = {n.id for n in page1}
    ids2 = {n.id for n in page2}
    ids3 = {n.id for n in page3}
    assert ids1.isdisjoint(ids2)
    assert ids1.isdisjoint(ids3)
    assert ids2.isdisjoint(ids3)


# ---------- find_unread_by_user_id ----------


def test_find_unread_by_user_id(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Route 15 was added",
            is_read=False,
        )
    )

    notifications = notification_repository.find_unread_by_user_id(1)

    assert len(notifications) == 1
    assert notifications[0].user_id == 1
    assert notifications[0].is_unread


def test_find_unread_by_user_id_excludes_read(
    notification_repository: SqlAlchemyNotificationRepository,
    route_repository: SqlAlchemyRouteRepository,
    subscription_repository: SqlAlchemySubscriptionRepository,
    agency: Agency,
    notification_parents: tuple[int, int],
) -> None:
    _, version_id = notification_parents
    assert agency.id is not None

    route_1 = route_repository.save(_make_route(agency.id, "1001"))
    route_2 = route_repository.save(_make_route(agency.id, "1002"))
    assert route_1.id is not None
    assert route_2.id is not None

    sub_1 = subscription_repository.save(_make_subscription(1, route_1.id))
    sub_2 = subscription_repository.save(_make_subscription(1, route_2.id))
    assert sub_1.id is not None
    assert sub_2.id is not None

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=sub_1.id,
            schedule_version_id=version_id,
            message="Unread",
            is_read=False,
        )
    )
    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=sub_2.id,
            schedule_version_id=version_id,
            message="Read",
            is_read=True,
        )
    )

    notifications = notification_repository.find_unread_by_user_id(1)

    assert len(notifications) == 1
    assert notifications[0].message == "Unread"
    assert notifications[0].is_unread


def test_find_unread_by_user_id_returns_empty_when_all_read(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="Read",
            is_read=True,
        )
    )

    assert notification_repository.find_unread_by_user_id(1) == []


def test_find_unread_by_user_id_returns_empty_list(
    notification_repository: SqlAlchemyNotificationRepository,
) -> None:
    assert notification_repository.find_unread_by_user_id(999) == []


def test_find_unread_by_user_id_does_not_leak_other_users(
    notification_repository: SqlAlchemyNotificationRepository,
    route_repository: SqlAlchemyRouteRepository,
    subscription_repository: SqlAlchemySubscriptionRepository,
    agency: Agency,
    notification_parents: tuple[int, int],
) -> None:
    _, version_id = notification_parents
    assert agency.id is not None

    route_1 = route_repository.save(_make_route(agency.id, "2001"))
    route_2 = route_repository.save(_make_route(agency.id, "2002"))
    assert route_1.id is not None
    assert route_2.id is not None

    sub_1 = subscription_repository.save(_make_subscription(1, route_1.id))
    sub_2 = subscription_repository.save(_make_subscription(2, route_2.id))
    assert sub_1.id is not None
    assert sub_2.id is not None

    notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=sub_1.id,
            schedule_version_id=version_id,
            message="Unread for user 1",
            is_read=False,
        )
    )
    notification_repository.save(
        _make_notification(
            user_id=2,
            subscription_id=sub_2.id,
            schedule_version_id=version_id,
            message="Unread for user 2",
            is_read=False,
        )
    )

    notifications = notification_repository.find_unread_by_user_id(1)

    assert len(notifications) == 1
    assert notifications[0].message == "Unread for user 1"


def test_find_unread_by_user_id_applies_pagination(
    notification_repository: SqlAlchemyNotificationRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, _ = notification_parents

    for i in range(3):
        version = _make_version(schedule_version_repository, f"unread-pagination-{i}")
        assert version.id is not None
        notification_repository.save(
            _make_notification(
                user_id=1,
                subscription_id=subscription_id,
                schedule_version_id=version.id,
                message=f"msg {i}",
                is_read=False,
            )
        )

    page1 = notification_repository.find_unread_by_user_id(1, offset=0, limit=2)
    page2 = notification_repository.find_unread_by_user_id(1, offset=2, limit=2)

    assert len(page1) == 2
    assert len(page2) == 1


# ---------- mark_as_read ----------


def test_mark_as_read_updates_notification(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents
    saved = notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="unread",
            is_read=False,
        )
    )
    assert saved.id is not None

    updated = notification_repository.mark_as_read(saved.id)

    assert updated is True
    assert notification_repository.find_unread_by_user_id(1) == []
    notifications = notification_repository.find_by_user_id(1)
    assert notifications[0].is_read is True


def test_mark_as_read_returns_false_for_unknown_id(
    notification_repository: SqlAlchemyNotificationRepository,
) -> None:
    assert notification_repository.mark_as_read(999999) is False


def test_mark_as_read_is_idempotent(
    notification_repository: SqlAlchemyNotificationRepository,
    notification_parents: tuple[int, int],
) -> None:
    subscription_id, version_id = notification_parents
    saved = notification_repository.save(
        _make_notification(
            user_id=1,
            subscription_id=subscription_id,
            schedule_version_id=version_id,
            message="x",
        )
    )
    assert saved.id is not None

    assert notification_repository.mark_as_read(saved.id) is True
    assert notification_repository.mark_as_read(saved.id) is True


# ---------- mark_all_as_read ----------


def test_mark_all_as_read_marks_only_user_notifications(
    notification_repository: SqlAlchemyNotificationRepository,
    route_repository: SqlAlchemyRouteRepository,
    subscription_repository: SqlAlchemySubscriptionRepository,
    schedule_version_repository: SqlAlchemyScheduleVersionRepository,
    agency: Agency,
) -> None:
    assert agency.id is not None

    route = route_repository.save(_make_route(agency.id, "300"))
    assert route.id is not None
    sub_1 = subscription_repository.save(_make_subscription(1, route.id))
    sub_2 = subscription_repository.save(_make_subscription(2, route.id))
    assert sub_1.id is not None
    assert sub_2.id is not None

    for i in range(3):
        version = _make_version(schedule_version_repository, f"mark-all-user1-{i}")
        assert version.id is not None
        notification_repository.save(
            _make_notification(
                user_id=1,
                subscription_id=sub_1.id,
                schedule_version_id=version.id,
                message="for user 1",
                is_read=False,
            )
        )

    v_user2 = _make_version(schedule_version_repository, "mark-all-user2")
    assert v_user2.id is not None
    notification_repository.save(
        _make_notification(
            user_id=2,
            subscription_id=sub_2.id,
            schedule_version_id=v_user2.id,
            message="for user 2",
            is_read=False,
        )
    )

    notification_repository.mark_all_as_read(1)

    assert notification_repository.find_unread_by_user_id(1) == []
    assert len(notification_repository.find_unread_by_user_id(2)) == 1


def test_mark_all_as_read_noop_for_user_without_notifications(
    notification_repository: SqlAlchemyNotificationRepository,
) -> None:
    notification_repository.mark_all_as_read(999)


def test_mark_all_as_read_does_not_touch_other_users(
    notification_repository: SqlAlchemyNotificationRepository,
    route_repository: SqlAlchemyRouteRepository,
    subscription_repository: SqlAlchemySubscriptionRepository,
    agency: Agency,
    notification_parents: tuple[int, int],
) -> None:
    _, version_id = notification_parents
    assert agency.id is not None

    route = route_repository.save(_make_route(agency.id, "400"))
    assert route.id is not None
    sub_2 = subscription_repository.save(_make_subscription(2, route.id))
    assert sub_2.id is not None

    notification_repository.save(
        _make_notification(
            user_id=2,
            subscription_id=sub_2.id,
            schedule_version_id=version_id,
            message="for user 2",
            is_read=False,
        )
    )

    notification_repository.mark_all_as_read(1)

    assert len(notification_repository.find_unread_by_user_id(2)) == 1
