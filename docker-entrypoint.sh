set -e

alembic upgrade head
exec "$@"
