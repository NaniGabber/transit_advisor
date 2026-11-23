from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Engine, inspect, text


def test_upgrade_adds_unique_index_to_legacy_schema(engine: Engine) -> None:
    migration_path = (
        Path(__file__).parents[2]
        / "alembic"
        / "versions"
        / "4f2c8a9d1e73_enforce_subscription_uniqueness.py"
    )
    spec = spec_from_file_location("subscription_uniqueness_migration", migration_path)
    assert spec is not None and spec.loader is not None
    migration = module_from_spec(spec)
    spec.loader.exec_module(migration)

    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(
                text("ALTER TABLE subscriptions DROP CONSTRAINT uq_user_route")
            )
            with Operations.context(MigrationContext.configure(connection)):
                migration.upgrade()

            indexes = inspect(connection).get_indexes("subscriptions")
            assert any(
                index["name"] == "uq_subscriptions_user_route" and index["unique"]
                for index in indexes
            )
        finally:
            transaction.rollback()
