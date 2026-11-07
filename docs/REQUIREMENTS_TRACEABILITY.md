# Requirements Traceability Matrix

## Purpose

This document maps the original project requirements to their implementation within the Transit Advisor system.

---

## Functional Requirements

| Requirement | Status | Implementation |
|------------|---------|---------------|
| GTFS feed import | ✅ Implemented | FeedUploadService, GtfsImportService |
| GTFS archive validation | ✅ Implemented | FeedValidator |
| Streaming archive processing | ✅ Implemented | GtfsArchiveReader |
| Checksum calculation | ✅ Implemented | ChecksumService |
| Duplicate feed detection | ✅ Implemented | ScheduleVersionService, `find_by_checksum` |
| Schedule version storage | ✅ Implemented | ScheduleVersion, ScheduleVersionRepository |
| Trip-to-version binding | ✅ Implemented | `Trip.schedule_version_id`, `GtfsImportService.import_all(..., schedule_version_id)` |
| Route comparison between versions | ✅ Implemented | `ScheduleDiffService.compare_versions`, `ScheduleUpdateService.compare_route_versions` |
| Timetable-level diff (stop times, added/removed stops) | ✅ Implemented | `ScheduleDiffService._diff_maps`, `_index_by_gtfs` |
| Route diff API | ✅ Implemented | `GET /routes/{id}/diff`, `RouteDiffResponse` |
| Route subscriptions | ✅ Implemented | SubscriptionService |
| User notifications | ✅ Implemented | NotificationService |
| Automatic notification generation | ✅ Implemented | ScheduleUpdateService |
| Feed upload API | ✅ Implemented | api/feeds.py |
| Subscription API | ✅ Implemented | api/subscriptions.py |
| Notification API | ✅ Implemented | api/notifications.py |
| Route search | ❌ Planned | Future work |
| Stop departures | ❌ Planned | Future work |
| Journey planning without transfers | ❌ Planned | Future work |
| Route timetable comparison | ✅ Implemented | `ScheduleDiffService.compare_versions`, `compare_route_versions` |
| Analytical reporting | ❌ Planned | Future work |

---

## Business Rules

| Rule | Status | Implementation |
|--------|---------|---------------|
| Duplicate GTFS feed must not create a new schedule version | ✅ Implemented | ChecksumService, ScheduleVersionService |
| Notification is generated only for subscribed routes | ✅ Implemented | ScheduleUpdateService |
| User cannot create duplicate subscriptions | ✅ Implemented | SubscriptionService |
| Routes must have valid identifiers | ✅ Implemented | Route entity validation |
| Notifications must contain a message | ✅ Implemented | Notification entity validation |
| ScheduleDiff cannot contain the same route in added and removed collections | ✅ Implemented | ScheduleDiff validation |
| One notification per subscription per change | ✅ Implemented | `ScheduleUpdateService.process_version_update` |
| Duplicate import returns the existing version, no re-import | ✅ Implemented | `FeedUploadService.upload`, `UploadResult(duplicate=True)` |
| Version comparison uses GTFS `trip_id`, not surrogate `Trip.id` | ✅ Implemented | ADR-002, `ScheduleDiffService._index_by_gtfs` |

---

## Non-Functional Requirements

| Requirement | Status | Implementation |
|------------|---------|---------------|
| Layered architecture | ✅ Implemented | API → Services → Repositories |
| Repository pattern | ✅ Implemented | Repository Protocols and SQLAlchemy implementations |
| Dependency Injection | ✅ Implemented | FastAPI dependencies (`api/dependencies.py`) |
| Database persistence | ✅ Implemented | PostgreSQL + SQLAlchemy (ADR-001) |
| Automated testing | ✅ Implemented | Unit, Integration and API tests |
| Documentation | ✅ Implemented | README, ARCHITECTURE, TESTING, REFACTORING, ADRs |
| Extensibility | ✅ Implemented | Protocol-based architecture |
| Transactional integrity (partial) | ⚠️ Partial | `flush()` in repositories; application-level transaction pending (see REFACTORING.md) |
| Import idempotency | ✅ Implemented | `ChecksumService` + `find_by_checksum` + `unique=True` |

---

## Testing Coverage

| Component | Status |
|------------|---------|
| Domain Entities | ✅ Tested |
| Service Layer | ✅ Tested |
| Repository Layer | ✅ Tested |
| API Layer | ✅ Tested |
| Validation Rules | ✅ Tested |
| Notification Workflow | ✅ Tested |
| Version Comparison (`compare_versions`) | ✅ Tested |
| Feed Import Idempotency | ✅ Tested |
| GTFS Mappers (`to_trip`, etc.) | ✅ Tested |
| Route Diff API | ✅ Tested |

---

## Future Work

The following requirements are identified for future development:

- route search by route number and stop;
- departure board for a selected stop;
- journey planning without transfers;
- transport analytics and reporting;
- application-level transactions for feed imports;
- structured logging;
- user authentication and authorization;
- email-based notifications;
- GTFS import performance optimisation (batch inserts, identifier caches).

---

## Summary

The implemented solution satisfies the core requirements related to:

- GTFS feed processing with idempotent re-import;
- schedule version management with trip-level binding;
- duplicate feed detection;
- version comparison at timetable level (stop times, added/removed stops);
- route subscriptions;
- change notifications (one per subscription per change);
- REST API integration, including `GET /routes/{id}/diff`;
- automated testing.

Additional route-searching, departure boards, journey planning, analytics and
reporting features are planned for future iterations.
