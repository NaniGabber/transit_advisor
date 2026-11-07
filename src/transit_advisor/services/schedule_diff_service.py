from typing import TypeVar

from transit_advisor.domain.route import Route
from transit_advisor.domain.schedulediff import ScheduleDiff
from transit_advisor.domain.stoptime import StopTime
from transit_advisor.domain.trip import Trip

TripKey = TypeVar("TripKey", int, str)


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

        old_map = self._index_by_pk(old_stop_times or [])
        new_map = self._index_by_pk(new_stop_times or [])
        changed_stop_times = self._diff_maps(
            old_map,
            new_map,
            trip_to_route or {},
        )

        return ScheduleDiff(
            added_routes=added_routes,
            removed_routes=removed_routes,
            changed_stop_times=changed_stop_times,
        )

    def compare_versions(
        self,
        old_trips: list[Trip],
        new_trips: list[Trip],
        old_stop_times: list[StopTime],
        new_stop_times: list[StopTime],
        trip_to_route: dict[str, str],
    ) -> ScheduleDiff:
        old_pk_to_gtfs = {t.id: t.trip_id for t in old_trips if t.id is not None}
        new_pk_to_gtfs = {t.id: t.trip_id for t in new_trips if t.id is not None}

        old_gtfs_ids = set(old_pk_to_gtfs.values())
        new_gtfs_ids = set(new_pk_to_gtfs.values())

        added_routes = sorted(
            {
                trip_to_route[t.trip_id]
                for t in new_trips
                if t.trip_id not in old_gtfs_ids and t.trip_id in trip_to_route
            }
        )
        removed_routes = sorted(
            {
                trip_to_route[t.trip_id]
                for t in old_trips
                if t.trip_id not in new_gtfs_ids and t.trip_id in trip_to_route
            }
        )

        old_map = self._index_by_gtfs(old_stop_times, old_pk_to_gtfs)
        new_map = self._index_by_gtfs(new_stop_times, new_pk_to_gtfs)
        changed_stop_times = self._diff_maps(
            old_map,
            new_map,
            trip_to_route,
        )

        return ScheduleDiff(
            added_routes=added_routes,
            removed_routes=removed_routes,
            changed_stop_times=changed_stop_times,
        )

    def _index_by_pk(
        self,
        stop_times: list[StopTime],
    ) -> dict[tuple[int, int], tuple[str, str]]:
        return {
            (st.trip_id, st.stop_id): (st.arrival_time, st.departure_time)
            for st in stop_times
        }

    def _index_by_gtfs(
        self,
        stop_times: list[StopTime],
        pk_to_gtfs: dict[int, str],
    ) -> dict[tuple[str, int], tuple[str, str]]:
        return {
            (pk_to_gtfs[st.trip_id], st.stop_id): (
                st.arrival_time,
                st.departure_time,
            )
            for st in stop_times
            if st.trip_id in pk_to_gtfs
        }

    def _diff_maps(
        self,
        old_map: dict[tuple[TripKey, int], tuple[str, str]],
        new_map: dict[tuple[TripKey, int], tuple[str, str]],
        trip_to_route: dict[TripKey, str],
    ) -> dict[str, list[int]]:
        changed: dict[str, list[int]] = {}
        for (trip_key, stop_id), new_times in new_map.items():
            old_times = old_map.get((trip_key, stop_id))
            if old_times != new_times:
                route_id = trip_to_route.get(trip_key)
                if route_id is not None:
                    changed.setdefault(route_id, []).append(stop_id)
        return changed
