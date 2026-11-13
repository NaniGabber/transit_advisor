#/bin/sh

docker compose exec db psql -U postgres -d transit -c "
SELECT 'agencies' AS table_name, count(*) FROM agencies \
UNION ALL SELECT 'routes', count(*) FROM routes \
UNION ALL SELECT 'stops', count(*) FROM stops \
UNION ALL SELECT 'trips', count(*) FROM trips \
UNION ALL SELECT 'stop_times', count(*) FROM stop_times \
UNION ALL SELECT 'schedule_versions', count(*) FROM schedule_versions \
ORDER BY table_name;
"
