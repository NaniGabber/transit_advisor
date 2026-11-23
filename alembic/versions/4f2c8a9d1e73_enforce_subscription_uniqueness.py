"""enforce unique user-route subscriptions

Revision ID: 4f2c8a9d1e73
Revises: 8d0af50a545f
Create Date: 2026-11-17 23:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4f2c8a9d1e73"
down_revision: str | Sequence[str] | None = "8d0af50a545f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_UNIQUE_INDEX_NAME = "uq_subscriptions_user_route"
_UNIQUE_COLUMNS = {"user_id", "route_id"}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    has_unique_constraint = any(
        set(constraint.get("column_names") or ()) == _UNIQUE_COLUMNS
        for constraint in inspector.get_unique_constraints("subscriptions")
    )
    has_unique_index = any(
        index.get("unique") and set(index.get("column_names") or ()) == _UNIQUE_COLUMNS
        for index in inspector.get_indexes("subscriptions")
    )

    if has_unique_constraint or has_unique_index:
        return

    duplicates_exist = bind.execute(
        sa.text(
            """
            SELECT 1
            FROM subscriptions
            GROUP BY user_id, route_id
            HAVING COUNT(*) > 1
            LIMIT 1
            """
        )
    ).first()
    if duplicates_exist:
        raise RuntimeError(
            "Cannot enforce unique user-route subscriptions: duplicate pairs "
            "already exist. Resolve them before upgrading."
        )

    op.create_index(
        _UNIQUE_INDEX_NAME,
        "subscriptions",
        ["user_id", "route_id"],
        unique=True,
    )


def downgrade() -> None:
    indexes = sa.inspect(op.get_bind()).get_indexes("subscriptions")
    if any(index["name"] == _UNIQUE_INDEX_NAME for index in indexes):
        op.drop_index(_UNIQUE_INDEX_NAME, table_name="subscriptions")
