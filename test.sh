#!/bin/sh
set -e

docker compose up -d

echo "Installing dependencies..."
docker exec -it transit_advisor-api-1 pip install -e '.[dev]'
echo "Running Ruff..."
docker exec -it transit_advisor-api-1 ruff check src tests scripts
echo "Running Mypy..."
docker exec -it transit_advisor-api-1 mypy src tests scripts
echo "Running Pytest..."
docker exec -it transit_advisor-api-1 pytest -q

echo "Running lint-import..."
docker exec -it transit_advisor-api-1 lint-imports

docker compose down
