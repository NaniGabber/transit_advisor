from transit_advisor.domain.route import Route
from transit_advisor.domain.schedulediff import ScheduleDiff
from transit_advisor.domain.stoptime import StopTime


class ScheduleDiffService:
    def compare_routes(
        self,
        old_routes: list[Route],
        new_routes: list[Route],
        old_stop_times: list[StopTime] | None = None,
        new_stop_times: list[StopTime] | None = None,
        trip_to_route: dict[int, str] | None = None,
    ) -> ScheduleDiff:
        old_ids = {route.route_id for route in old_routes}
        new_ids = {route.route_id for route in new_routes}

        added_routes = sorted(new_ids - old_ids)
        removed_routes = sorted(old_ids - new_ids)

        changed_stop_times = self._compare_stop_times(
            old_stop_times or [],
            new_stop_times or [],
            trip_to_route or {},
        )

        return ScheduleDiff(
            added_routes=added_routes,
            removed_routes=removed_routes,
            changed_stop_times=changed_stop_times,
        )

    def _compare_stop_times(
        self,
        old_stop_times: list[StopTime],
        new_stop_times: list[StopTime],
        trip_to_route: dict[int, str],
    ) -> dict[str, list[int]]:
        old_map = {
            (st.trip_id, st.stop_id): (st.arrival_time, st.departure_time)
            for st in old_stop_times
        }
        new_map = {
            (st.trip_id, st.stop_id): (st.arrival_time, st.departure_time)
            for st in new_stop_times
        }

        changed: dict[str, list[int]] = {}

        for (trip_id, stop_id), new_times in new_map.items():
            old_times = old_map.get((trip_id, stop_id))
            if old_times != new_times:
                route_id = trip_to_route.get(trip_id)
                if route_id is not None:
                    changed.setdefault(route_id, []).append(stop_id)

        return changed
