#!/bin/sh

set -e

cleanup() {
    docker compose down
}

trap cleanup EXIT

docker compose up -d

echo "Installing dependencies..."
docker compose exec api pip install -e ".[dev]"

echo "Alembic migration..."
docker compose exec api alembic upgrade head

echo "Running Ruff..."
docker compose exec api ruff check src tests scripts

echo "Running Mypy..."
docker compose exec api mypy src tests scripts

echo "Running Pytest..."
docker compose exec api pytest -q

echo "Running lint-imports..."
docker compose exec api lint-imports
