import pytest

from transit_advisor.domain.subscription import (
    Subscription,
)


@pytest.mark.parametrize(
    "user_id, route_id",
    [
        (0, "11"),
        (-1, "11"),
        (1, ""),
    ],
)
def test_invalid_subscription_rejected(
    user_id: int,
    route_id: str,
) -> None:
    with pytest.raises(ValueError):
        Subscription(
            id=None,
            user_id=user_id,
            route_id=route_id,
        )


def test_create_valid_subscription() -> None:
    subscription = Subscription(
        id=None,
        user_id=1,
        route_id="11",
    )

    assert subscription.user_id == 1
    assert subscription.route_id == "11"


def test_create_subscription_with_existing_id() -> None:
    subscription = Subscription(
        id=5,
        user_id=1,
        route_id="11",
    )

    assert subscription.id == 5
