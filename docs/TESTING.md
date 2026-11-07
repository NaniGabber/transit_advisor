# Testing Report

## Result

PASSED

## Coverage Overview

- **Total coverage:** 92%
- **Statements:** 1087
- **Covered lines:** 998
- **Missing lines:** 89
- **Excluded lines:** 0

## Coverage by File

| File | Statements | Missing | Coverage |
|------|-----------:|--------:|---------:|
| `src/transit_advisor/__init__.py` | 1 | 0 | 100% |
| `src/transit_advisor/api/dependencies.py` | 61 | 14 | 77% |
| `src/transit_advisor/api/feeds.py` | 31 | 1 | 97% |
| `src/transit_advisor/api/notification.py` | 13 | 0 | 100% |
| `src/transit_advisor/api/schemas.py` | 29 | 0 | 100% |
| `src/transit_advisor/api/subscription.py` | 17 | 0 | 100% |
| `src/transit_advisor/domain/__init__.py` | 9 | 0 | 100% |
| `src/transit_advisor/domain/agency.py` | 22 | 2 | 91% |
| `src/transit_advisor/domain/notification.py` | 25 | 1 | 96% |
| `src/transit_advisor/domain/repositories/agency.py` | 5 | 0 | 100% |
| `src/transit_advisor/domain/repositories/notification.py` | 6 | 0 | 100% |
| `src/transit_advisor/domain/repositories/route.py` | 6 | 0 | 100% |
| `src/transit_advisor/domain/repositories/scheduleversion.py` | 5 | 0 | 100% |
| `src/transit_advisor/domain/repositories/stop.py` | 5 | 0 | 100% |
| `src/transit_advisor/domain/repositories/stoptime.py` | 8 | 0 | 100% |
| `src/transit_advisor/domain/repositories/subscription.py` | 6 | 0 | 100% |
| `src/transit_advisor/domain/repositories/trip.py` | 6 | 0 | 100% |
| `src/transit_advisor/domain/route.py` | 39 | 3 | 92% |
| `src/transit_advisor/domain/schedulediff.py` | 13 | 0 | 100% |
| `src/transit_advisor/domain/scheduleversion.py` | 15 | 1 | 93% |
| `src/transit_advisor/domain/stop.py` | 26 | 3 | 88% |
| `src/transit_advisor/domain/stoptime.py` | 23 | 1 | 96% |
| `src/transit_advisor/domain/subscription.py` | 15 | 1 | 93% |
| `src/transit_advisor/domain/trip.py` | 20 | 3 | 85% |
| `src/transit_advisor/domain/upload_result.py` | 6 | 0 | 100% |
| `src/transit_advisor/infrastructure/archive/gtfs_archive_reader.py` | 17 | 2 | 88% |
| `src/transit_advisor/infrastructure/database/base.py` | 8 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/__init__.py` | 9 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/agency.py` | 13 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/notification.py` | 14 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/route.py` | 15 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/scheduleversion.py` | 9 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/stop.py` | 12 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/stoptime.py` | 11 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/subscription.py` | 10 | 0 | 100% |
| `src/transit_advisor/infrastructure/database/models/trip.py` | 10 | 0 | 100% |
| `src/transit_advisor/infrastructure/gtfs/mappers/agency.py` | 10 | 0 | 100% |
| `src/transit_advisor/infrastructure/gtfs/mappers/route.py` | 10 | 0 | 100% |
| `src/transit_advisor/infrastructure/gtfs/mappers/stop.py` | 11 | 0 | 100% |
| `src/transit_advisor/infrastructure/gtfs/mappers/stoptime.py` | 10 | 0 | 100% |
| `src/transit_advisor/infrastructure/gtfs/mappers/trip.py` | 7 | 0 | 100% |
| `src/transit_advisor/infrastructure/gtfs/parsing.py` | 12 | 0 | 100% |
| `src/transit_advisor/infrastructure/repositories/agency.py` | 19 | 0 | 100% |
| `src/transit_advisor/infrastructure/repositories/notification.py` | 21 | 11 | 48% |
| `src/transit_advisor/infrastructure/repositories/route.py` | 26 | 0 | 100% |
| `src/transit_advisor/infrastructure/repositories/scheduleversion.py` | 19 | 0 | 100% |
| `src/transit_advisor/infrastructure/repositories/stop.py` | 19 | 0 | 100% |
| `src/transit_advisor/infrastructure/repositories/stoptime.py` | 30 | 8 | 73% |
| `src/transit_advisor/infrastructure/repositories/subscription.py` | 27 | 0 | 100% |
| `src/transit_advisor/infrastructure/repositories/trip.py` | 24 | 2 | 92% |
| `src/transit_advisor/main.py` | 8 | 8 | 0% |
| `src/transit_advisor/services/__init__.py` | 0 | 0 | 100% |
| `src/transit_advisor/services/checksum_service.py` | 11 | 0 | 100% |
| `src/transit_advisor/services/feed_upload_service.py` | 24 | 0 | 100% |
| `src/transit_advisor/services/feed_validation_service.py` | 6 | 0 | 100% |
| `src/transit_advisor/services/gtfs_import_service.py` | 106 | 13 | 88% |
| `src/transit_advisor/services/notification_service.py` | 22 | 1 | 95% |
| `src/transit_advisor/services/schedule_diff_service.py` | 40 | 0 | 100% |
| `src/transit_advisor/services/schedule_update_service.py` | 64 | 14 | 78% |
| `src/transit_advisor/services/schedule_version_service.py` | 11 | 0 | 100% |
| `src/transit_advisor/services/subscription_service.py` | 10 | 0 | 100% |

## Uncovered Lines

- `src/transit_advisor/api/dependencies.py`: 49, 50, 51, 53, 59, 65, 71, 77, 83, 108, 131, 140, 148, 172
- `src/transit_advisor/api/feeds.py`: 37
- `src/transit_advisor/domain/agency.py`: 28, 31
- `src/transit_advisor/domain/notification.py`: 30
- `src/transit_advisor/domain/route.py`: 33, 36, 39
- `src/transit_advisor/domain/scheduleversion.py`: 21
- `src/transit_advisor/domain/stop.py`: 25, 28, 38
- `src/transit_advisor/domain/stoptime.py`: 34
- `src/transit_advisor/domain/subscription.py`: 22
- `src/transit_advisor/domain/trip.py`: 22, 25, 29
- `src/transit_advisor/infrastructure/archive/gtfs_archive_reader.py`: 33, 34
- `src/transit_advisor/infrastructure/repositories/notification.py`: 23, 32, 33, 34, 36, 50, 56, 60, 77, 84, 88
- `src/transit_advisor/infrastructure/repositories/stoptime.py`: 50, 51, 52, 57, 60, 65, 72, 81
- `src/transit_advisor/infrastructure/repositories/trip.py`: 51, 54
- `src/transit_advisor/main.py`: 1, 3, 6, 9, 13, 15, 19, 23
- `src/transit_advisor/services/gtfs_import_service.py`: 38, 40, 41, 45, 46, 50, 51, 55, 56, 61, 62, 66, 217
- `src/transit_advisor/services/notification_service.py`: 55
- `src/transit_advisor/services/schedule_update_service.py`: 109, 132, 133, 134, 136, 137, 139, 140, 142, 145, 149, 150, 151, 153

## Environment

Generated automatically from pytest + pytest-cov results.
Raw report: `tests/result.json`
