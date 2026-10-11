import pytest

from transit_advisor.domain.subscription import Subscription


@pytest.mark.parametrize(
    "user_id, route_id",
    [
        (0, 1),
        (-1, 1),
        (1, 0),
        (1, -1),
    ],
)
def test_invalid_subscription_rejected(
    user_id: int,
    route_id: int,
) -> None:
    with pytest.raises(ValueError):
        Subscription(
            id=None,
            user_id=user_id,
            route_id=route_id,
        )
