from transit_advisor.domain.route import Route
from transit_advisor.domain.schedulediff import ScheduleDiff


class ScheduleDiffService:
    def compare_routes(
        self,
        old_routes: list[Route],
        new_routes: list[Route],
    ) -> ScheduleDiff:
        old_ids = {route.route_id for route in old_routes}

        new_ids = {route.route_id for route in new_routes}

        added_routes = sorted(
            new_ids - old_ids,
        )

        removed_routes = sorted(
            old_ids - new_ids,
        )

        return ScheduleDiff(
            added_routes=added_routes,
            removed_routes=removed_routes,
        )
