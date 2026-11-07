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
| Duplicate feed detection | ✅ Implemented | ScheduleVersionService |
| Schedule version storage | ✅ Implemented | ScheduleVersion, ScheduleVersionRepository |
| Route comparison between versions | ✅ Partially Implemented | ScheduleDiffService |
| Route subscriptions | ✅ Implemented | SubscriptionService |
| User notifications | ✅ Implemented | NotificationService |
| Automatic notification generation | ✅ Implemented | ScheduleUpdateService |
| Feed upload API | ✅ Implemented | api/feeds.py |
| Subscription API | ✅ Implemented | api/subscriptions.py |
| Notification API | ✅ Implemented | api/notifications.py |
| Route search | ❌ Planned | Future work |
| Stop departures | ❌ Planned | Future work |
| Journey planning without transfers | ❌ Planned | Future work |
| Route timetable comparison | ❌ Planned | Future work |
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

---

## Non-Functional Requirements

| Requirement | Status | Implementation |
|------------|---------|---------------|
| Layered architecture | ✅ Implemented | API → Services → Repositories |
| Repository pattern | ✅ Implemented | Repository Protocols and SQLAlchemy implementations |
| Dependency Injection | ✅ Implemented | FastAPI dependencies |
| Database persistence | ✅ Implemented | PostgreSQL + SQLAlchemy |
| Automated testing | ✅ Implemented | Unit, Integration and API tests |
| Documentation | ✅ Implemented | README, ARCHITECTURE, TESTING |
| Extensibility | ✅ Implemented | Protocol-based architecture |

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

---

## Future Work

The following requirements are identified for future development:

- route search by route number and stop;
- departure board for a selected stop;
- route comparison at timetable level;
- journey planning without transfers;
- transport analytics and reporting;
- user authentication and authorization;
- email-based notifications.

---

## Summary

The implemented solution satisfies the core requirements related to:

- GTFS feed processing;
- schedule version management;
- duplicate feed detection;
- route subscriptions;
- change notifications;
- REST API integration;
- automated testing.

Additional route-searching, timetable analysis and reporting features are planned for future iterations.
