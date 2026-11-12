from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from transit_advisor.infrastructure.database.models.scheduleversion import (
    ScheduleVersionModel,
)
from transit_advisor.infrastructure.database.models.stoptime import StopTimeModel
from transit_advisor.infrastructure.database.models.trip import TripModel


class SqlAlchemyAnalyticsRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _latest_version_id(self) -> int | None:
        statement = (
            select(ScheduleVersionModel.id)
            .order_by(ScheduleVersionModel.imported_at.desc())
            .limit(1)
        )
        return self._session.scalar(statement)

    def count_trips_by_day(self, route_id: int) -> dict[str, int]:
        version_id = self._latest_version_id()
        if version_id is None:
            return {}

        statement = (
            select(TripModel.service_id, func.count(TripModel.id))
            .where(
                TripModel.route_id == route_id,
                TripModel.schedule_version_id == version_id,
            )
            .group_by(TripModel.service_id)
        )
        results = self._session.execute(statement).all()
        return {service_id: count for service_id, count in results}

    def average_headway_minutes(self, route_id: int) -> float | None:
        version_id = self._latest_version_id()
        if version_id is None:
            return None

        statement = (
            select(StopTimeModel.departure_time)
            .join(TripModel, StopTimeModel.trip_id == TripModel.id)
            .where(
                TripModel.route_id == route_id,
                TripModel.schedule_version_id == version_id,
            )
            .order_by(StopTimeModel.departure_time)
        )
        times = [row[0] for row in self._session.execute(statement).all()]
        if len(times) < 2:
            return None

        def parse(t: str) -> datetime:
            return datetime.strptime(t, "%H:%M:%S")

        diffs = []
        for i in range(1, len(times)):
            diff = parse(times[i]) - parse(times[i - 1])
            diffs.append(diff.total_seconds() / 60)

        return sum(diffs) / len(diffs) if diffs else None

    def top_stops(self, limit: int = 10) -> list[tuple[int, int]]:
        version_id = self._latest_version_id()
        if version_id is None:
            return []

        statement = (
            select(
                StopTimeModel.stop_id,
                func.count(func.distinct(TripModel.route_id)),
            )
            .join(TripModel, StopTimeModel.trip_id == TripModel.id)
            .where(TripModel.schedule_version_id == version_id)
            .group_by(StopTimeModel.stop_id)
            .order_by(func.count(func.distinct(TripModel.route_id)).desc())
            .limit(limit)
        )
        results = self._session.execute(statement).all()
        return [(stop_id, count) for stop_id, count in results]
