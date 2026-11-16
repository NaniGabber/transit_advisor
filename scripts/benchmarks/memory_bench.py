import os
import subprocess
import tracemalloc
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from transit_advisor.main import app

ADMIN_DATABASE_URL = "postgresql+psycopg://postgres:postgres@db:5432/postgres"


def main() -> None:
    db_name = f"transit_benchmark_{uuid.uuid4().hex[:8]}"

    database_url = f"postgresql+psycopg://postgres:postgres@db:5432/{db_name}"

    admin_engine = create_engine(
        ADMIN_DATABASE_URL,
        isolation_level="AUTOCOMMIT",
    )

    try:
        print(f"Creating database {db_name}")

        with admin_engine.connect() as conn:
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))

        env = os.environ.copy()
        env["DATABASE_URL"] = database_url

        print("Running migrations...")

        subprocess.run(
            ["alembic", "upgrade", "head"],
            env=env,
            check=True,
        )

        print("Running benchmark...")

        os.environ["DATABASE_URL"] = database_url

        client = TestClient(app)

        with open("data/static.zip", "rb") as file:
            tracemalloc.start()

            response = client.post(
                "/api/v1/imports/gtfs",
                headers={"X-Role": "admin"},
                files={
                    "file": (
                        "static.zip",
                        file.read(),
                        "application/zip",
                    )
                },
            )

            current, peak = tracemalloc.get_traced_memory()

            tracemalloc.stop()

        print()
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"Current memory: {current / 1024 / 1024:.2f} MB")
        print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")

    finally:
        print(f"Removing database {db_name}")

        with admin_engine.connect() as conn:
            conn.execute(
                text(
                    """
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = :dbname
                      AND pid <> pg_backend_pid()
                    """
                ),
                {"dbname": db_name},
            )

            conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}"'))

        admin_engine.dispose()


if __name__ == "__main__":
    main()
