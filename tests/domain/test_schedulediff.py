import pytest

from transit_advisor.domain.schedulediff import (
    ScheduleDiff,
)


@pytest.fixture
def schedule_diff() -> ScheduleDiff:
    return ScheduleDiff(
        added_routes=["11"],
        removed_routes=["15"],
    )


def test_create_valid_schedule_diff(
    schedule_diff: ScheduleDiff,
) -> None:
    assert schedule_diff.added_routes == ["11"]
    assert schedule_diff.removed_routes == ["15"]


@pytest.mark.parametrize(
    "added_routes, removed_routes",
    [
        ([""], []),
        (["11", ""], []),
        ([], [""]),
        ([], ["15", ""]),
        ([" "], []),
        ([], [" "]),
    ],
)
def test_empty_route_id_rejected(
    added_routes: list[str],
    removed_routes: list[str],
) -> None:
    with pytest.raises(ValueError):
        ScheduleDiff(
            added_routes=added_routes,
            removed_routes=removed_routes,
        )


def test_route_cannot_be_added_and_removed() -> None:
    with pytest.raises(ValueError):
        ScheduleDiff(
            added_routes=["11"],
            removed_routes=["11"],
        )


def test_empty_diff_is_valid() -> None:
    diff = ScheduleDiff(
        added_routes=[],
        removed_routes=[],
    )

    assert diff.added_routes == []
    assert diff.removed_routes == []
