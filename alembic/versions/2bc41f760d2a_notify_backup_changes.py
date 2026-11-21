"""notify the backup worker about committed application data changes

Revision ID: 2bc41f760d2a
Revises: 4f2c8a9d1e73
Create Date: 2026-11-21 17:35:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "2bc41f760d2a"
down_revision: str | Sequence[str] | None = "4f2c8a9d1e73"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLES = (
    "agencies",
    "routes",
    "stops",
    "trips",
    "stop_times",
    "schedule_versions",
    "subscriptions",
    "notifications",
)


def upgrade() -> None:
    op.execute(
        """
        CREATE FUNCTION notify_transit_advisor_backup_change()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            PERFORM pg_notify('transit_advisor_backup', TG_TABLE_NAME);
            RETURN NULL;
        END;
        $$;
        """
    )
    for table in _TABLES:
        op.execute(
            f"""
            CREATE TRIGGER notify_backup_change
            AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON "{table}"
            FOR EACH STATEMENT
            EXECUTE FUNCTION notify_transit_advisor_backup_change();
            """
        )


def downgrade() -> None:
    for table in _TABLES:
        op.execute(f'DROP TRIGGER notify_backup_change ON "{table}"')
    op.execute("DROP FUNCTION notify_transit_advisor_backup_change()")
