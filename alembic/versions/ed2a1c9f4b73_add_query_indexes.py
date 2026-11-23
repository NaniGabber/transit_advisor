"""add query indexes

Revision ID: ed2a1c9f4b73
Revises: 2bc41f760d2a
Create Date: 2026-11-21 21:57:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "ed2a1c9f4b73"
down_revision: str | Sequence[str] | None = "2bc41f760d2a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index("ix_routes_agency_id", "routes", ["agency_id"])
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.create_index(
        "ix_routes_route_id_trgm",
        "routes",
        ["route_id"],
        postgresql_using="gin",
        postgresql_ops={"route_id": "gin_trgm_ops"},
    )
    op.create_index(
        "ix_routes_short_name_trgm",
        "routes",
        ["short_name"],
        postgresql_using="gin",
        postgresql_ops={"short_name": "gin_trgm_ops"},
    )
    op.create_index(
        "ix_routes_long_name_trgm",
        "routes",
        ["long_name"],
        postgresql_using="gin",
        postgresql_ops={"long_name": "gin_trgm_ops"},
    )

    op.create_index("ix_trips_trip_id", "trips", ["trip_id"])
    op.create_index("ix_trips_route_id", "trips", ["route_id"])
    op.create_index(
        "ix_trips_schedule_version_id",
        "trips",
        ["schedule_version_id"],
    )
    op.create_index(
        "ix_trips_route_schedule_service",
        "trips",
        ["route_id", "schedule_version_id", "service_id"],
    )

    op.execute(
        """
        DELETE FROM stop_times
        WHERE id IN (
            SELECT id
            FROM (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY trip_id, stop_sequence
                        ORDER BY id
                    ) AS duplicate_number
                FROM stop_times
            ) ranked
            WHERE duplicate_number > 1
        )
        """
    )
    op.create_unique_constraint(
        "uq_stop_times_trip_sequence",
        "stop_times",
        ["trip_id", "stop_sequence"],
    )
    op.create_index(
        "ix_stop_times_stop_departure",
        "stop_times",
        ["stop_id", "departure_time"],
    )
    op.create_index(
        "ix_stop_times_stop_arrival",
        "stop_times",
        ["stop_id", "arrival_time"],
    )
    op.create_index(
        "ix_stop_times_stop_trip",
        "stop_times",
        ["stop_id", "trip_id"],
    )

    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])

    op.create_index(
        "ix_notifications_user_read_created",
        "notifications",
        ["user_id", "is_read", "created_at"],
    )
    op.create_index(
        "ix_notifications_subscription_id",
        "notifications",
        ["subscription_id"],
    )
    op.create_index(
        "ix_notifications_schedule_version_id",
        "notifications",
        ["schedule_version_id"],
    )

    op.create_index(
        "ix_schedule_versions_imported_at",
        "schedule_versions",
        ["imported_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_schedule_versions_imported_at",
        table_name="schedule_versions",
    )
    op.drop_index(
        "ix_notifications_schedule_version_id",
        table_name="notifications",
    )
    op.drop_index(
        "ix_notifications_subscription_id",
        table_name="notifications",
    )
    op.drop_index(
        "ix_notifications_user_read_created",
        table_name="notifications",
    )
    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_index("ix_stop_times_stop_trip", table_name="stop_times")
    op.drop_index("ix_stop_times_stop_arrival", table_name="stop_times")
    op.drop_index("ix_stop_times_stop_departure", table_name="stop_times")
    op.drop_constraint(
        "uq_stop_times_trip_sequence",
        "stop_times",
        type_="unique",
    )
    op.drop_index(
        "ix_trips_route_schedule_service",
        table_name="trips",
    )
    op.drop_index("ix_trips_schedule_version_id", table_name="trips")
    op.drop_index("ix_trips_route_id", table_name="trips")
    op.drop_index("ix_trips_trip_id", table_name="trips")
    op.drop_index("ix_routes_long_name_trgm", table_name="routes")
    op.drop_index("ix_routes_short_name_trgm", table_name="routes")
    op.drop_index("ix_routes_route_id_trgm", table_name="routes")
    op.drop_index("ix_routes_agency_id", table_name="routes")
