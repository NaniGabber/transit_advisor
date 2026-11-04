from transit_advisor.api.dependencies import (
    get_checksum_service,
    get_feed_validator,
    get_notification_repository,
    get_notification_service,
    get_subscription_repository,
    get_subscription_service,
)
from transit_advisor.services.checksum_service import (
    ChecksumService,
)
from transit_advisor.services.feed_validation_service import (
    FeedValidator,
)
from transit_advisor.services.notification_service import NotificationService
from transit_advisor.services.subscription_service import SubscriptionService


def test_get_feed_validator() -> None:
    service = get_feed_validator()

    assert isinstance(
        service,
        FeedValidator,
    )


def test_get_checksum_service() -> None:
    service = get_checksum_service()

    assert isinstance(
        service,
        ChecksumService,
    )


def test_get_notification_service(
    session,
) -> None:
    repository = get_notification_repository(
        session,
    )

    service = get_notification_service(
        repository,
    )

    assert isinstance(
        service,
        NotificationService,
    )


def test_get_subscription_service(
    session,
) -> None:
    repository = get_subscription_repository(
        session,
    )

    service = get_subscription_service(
        repository,
    )

    assert isinstance(
        service,
        SubscriptionService,
    )
