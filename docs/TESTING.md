# Testing Report

## Result

PASSED

## Coverage Overview

- **Total coverage:** 95%
- **Statements:** 2058
- **Covered lines:** 1964
- **Missing lines:** 94
- **Excluded lines:** 0

## Coverage by File

| File | Statements | Missing | Coverage |
|------|-----------:|--------:|---------:|
| `src/transit_advisor/__init__.py` | 1 | 0 | 100% |
| `src/transit_advisor/api/__init__.py` | 0 | 0 | 100% |
| `src/transit_advisor/api/analytics.py` | 17 | 0 | 100% |
| `src/transit_advisor/api/auth.py` | 16 | 0 | 100% |
| `src/transit_advisor/api/database_transfer.py` | 34 | 0 | 100% |
| `src/transit_advisor/api/dependencies.py` | 81 | 4 | 95% |
| `src/transit_advisor/api/feeds.py` | 38 | 2 | 95% |
| `src/transit_advisor/api/journeys.py` | 11 | 0 | 100% |
| `src/transit_advisor/api/notification.py` | 13 | 0 | 100% |
| `src/transit_advisor/api/routes.py` | 19 | 0 | 100% |
| `src/transit_advisor/api/schemas.py` | 67 | 0 | 100% |
| `src/transit_advisor/api/stops.py` | 19 | 0 | 100% |
| `src/transit_advisor/api/subscription.py` | 26 | 2 | 92% |
| `src/transit_advisor/domain/__init__.py` | 9 | 0 | 100% |
| `src/transit_advisor/domain/agency.py` | 22 | 2 | 91% |
| `src/transit_advisor/domain/exceptions.py` | 21 | 0 | 100% |
| `src/transit_advisor/domain/journey.py` | 10 | 0 | 100% |
| `src/transit_advisor/domain/notification.py` | 25 | 1 | 96% |
| `src/transit_advisor/domain/repositories/agency.py` | 7 | 0 | 100% |
| `src/transit_advisor/domain/repositories/database_transfer.py` | 6 | 0 | 100% |
| `src/transit_advisor/domain/repositories/notification.py` | 6 | 0 | 100% |
| `src/transit_advisor/domain/repositories/route.py` | 9 | 0 | 100% |
| `src/transit_advisor/domain/repositories/scheduleversion.py` | 6 | 0 | 100% |
| `src/transit_advisor/domain/repositories/stop.py` | 7 | 0 | 100% |
| `src/transit_advisor/domain/repositories/stoptime.py` | 12 | 0 | 100% |
| `src/transit_advisor/domain/repositories/subscription.py` | 10 | 0 | 100% |
| `src/transit_advisor/domain/repositories/trip.py` | 9 | 0 | 100% |
| `src/transit_advisor/domain/route.py` | 39 | 3 | 92% |
| `src/transit_advisor/domain/schedulediff.py` | 13 | 0 | 100% |
| `src/transit_advisor/domain/scheduleversion.py` | 15 | 1 | 93% |
| `src/transit_advisor/domain/stop.py` | 26 | 3 | 88% |
| `src/transit_advisor/domain/stoptime.py` | 23 | 1 | 96% |
| `src/transit_advisor/domain/subscription.py` | 15 | 1 | 93% |
| `src/transit_advisor/domain/trip.py` | 21 | 3 | 86% |
| `src/transit_advisor/domain/upload_result.py` | 11 | 0 | 100% |
| `src/transit_advisor/infrastructure/__init__.py` | 0 | 0 | 100% |
| `src/transit_advisor/infrastructure/archive/gtfs_archive_reader.py` | 17 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/base.py` | 8 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/__init__.py` | 9 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/agency.py` | 13 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/notification.py` | 14 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/route.py` | 17 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/scheduleversion.py` | 10 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/stop.py` | 13 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/stoptime.py` | 14 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/subscription.py` | 10 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/trip.py` | 14 | 0 | 100% |
| `src/transit_advisor/infrastructure/gtfs/mappers/agency.py` | 10 | 0 | 100% |
| `src/transit_advisor/infrastructure/gtfs/mappers/route.py` | 13 | 2 | 85% |
| `src/transit_advisor/infrastructure/gtfs/mappers/stop.py` | 14 | 2 | 86% |
| `src/transit_advisor/infrastructure/gtfs/mappers/stoptime.py` | 13 | 2 | 85% |
| `src/transit_advisor/infrastructure/gtfs/mappers/trip.py` | 8 | 0 | 100% |
| `src/transit_advisor/infrastructure/gtfs/parsing.py` | 12 | 0 | 100% |
| `src/transit_advisor/infrastructure/repositories/agency.py` | 34 | 5 | 85% |
| `src/transit_advisor/infrastructure/repositories/analytics.py` | 41 | 0 | 100% |
| `src/transit_advisor/infrastructure/repositories/database_transfer.py` | 72 | 0 | 100% |
| `src/transit_advisor/infrastructure/repositories/notification.py` | 43 | 0 | 100% |
| `src/transit_advisor/infrastructure/repositories/route.py` | 51 | 5 | 90% |
| `src/transit_advisor/infrastructure/repositories/scheduleversion.py` | 32 | 0 | 100% |
| `src/transit_advisor/infrastructure/repositories/stop.py` | 34 | 5 | 85% |
| `src/transit_advisor/infrastructure/repositories/stoptime.py` | 57 | 5 | 91% |
| `src/transit_advisor/infrastructure/repositories/subscription.py` | 44 | 3 | 93% |
| `src/transit_advisor/infrastructure/repositories/trip.py` | 43 | 5 | 88% |
| `src/transit_advisor/logging_config.py` | 10 | 3 | 70% |
| `src/transit_advisor/main.py` | 48 | 0 | 100% |
| `src/transit_advisor/rate_limit.py` | 44 | 7 | 84% |
| `src/transit_advisor/services/__init__.py` | 0 | 0 | 100% |
| `src/transit_advisor/services/analytics_service.py` | 18 | 0 | 100% |
| `src/transit_advisor/services/backup_service.py` | 73 | 21 | 71% |
| `src/transit_advisor/services/checksum_service.py` | 19 | 0 | 100% |
| `src/transit_advisor/services/database_transfer_service.py` | 46 | 0 | 100% |
| `src/transit_advisor/services/feed_upload_service.py` | 42 | 1 | 98% |
| `src/transit_advisor/services/feed_validation_service.py` | 11 | 0 | 100% |
| `src/transit_advisor/services/gtfs_import_service.py` | 188 | 0 | 100% |
| `src/transit_advisor/services/journey_service.py` | 14 | 0 | 100% |
| `src/transit_advisor/services/notification_service.py` | 27 | 1 | 96% |
| `src/transit_advisor/services/schedule_diff_service.py` | 45 | 0 | 100% |
| `src/transit_advisor/services/schedule_update_service.py` | 76 | 1 | 99% |
| `src/transit_advisor/services/schedule_version_service.py` | 23 | 0 | 100% |
| `src/transit_advisor/services/subscription_service.py` | 33 | 1 | 97% |
| `src/transit_advisor/settings.py` | 17 | 2 | 88% |

## Uncovered Lines

- `src/transit_advisor/api/dependencies.py`: 64, 65, 66, 67
- `src/transit_advisor/api/feeds.py`: 47, 48
- `src/transit_advisor/api/subscription.py`: 47, 58
- `src/transit_advisor/domain/agency.py`: 28, 31
- `src/transit_advisor/domain/notification.py`: 30
- `src/transit_advisor/domain/route.py`: 33, 36, 39
- `src/transit_advisor/domain/scheduleversion.py`: 22
- `src/transit_advisor/domain/stop.py`: 25, 28, 38
- `src/transit_advisor/domain/stoptime.py`: 34
- `src/transit_advisor/domain/subscription.py`: 22
- `src/transit_advisor/domain/trip.py`: 23, 26, 30
- `src/transit_advisor/infrastructure/gtfs/mappers/route.py`: 11, 12
- `src/transit_advisor/infrastructure/gtfs/mappers/stop.py`: 14, 15
- `src/transit_advisor/infrastructure/gtfs/mappers/stoptime.py`: 14, 15
- `src/transit_advisor/infrastructure/repositories/agency.py`: 24, 41, 42, 43, 46
- `src/transit_advisor/infrastructure/repositories/route.py`: 23, 40, 41, 42, 45
- `src/transit_advisor/infrastructure/repositories/stop.py`: 24, 41, 42, 43, 46
- `src/transit_advisor/infrastructure/repositories/stoptime.py`: 24, 61, 70, 112, 117
- `src/transit_advisor/infrastructure/repositories/subscription.py`: 35, 80, 81
- `src/transit_advisor/infrastructure/repositories/trip.py`: 26, 64, 65, 67, 70
- `src/transit_advisor/logging_config.py`: 12, 13, 19
- `src/transit_advisor/rate_limit.py`: 27, 28, 29, 33, 49, 54, 55
- `src/transit_advisor/services/backup_service.py`: 32, 33, 34, 35, 36, 39, 41, 54, 55, 56, 57, 61, 62, 63, 95, 99, 100, 101, 102, 107, 111
- `src/transit_advisor/services/feed_upload_service.py`: 55
- `src/transit_advisor/services/notification_service.py`: 67
- `src/transit_advisor/services/schedule_update_service.py`: 142
- `src/transit_advisor/services/subscription_service.py`: 67
- `src/transit_advisor/settings.py`: 15, 16

## Environment

Generated automatically from pytest + pytest-cov results.
Raw report: `tests/result.json`
