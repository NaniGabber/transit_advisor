# Architecture

## Overview

Transit Advisor is a backend information system for processing GTFS transit feeds, tracking schedule versions, detecting schedule changes and notifying subscribed users about updates.

The system is designed according to Clean Architecture principles. Business rules are isolated from infrastructure concerns, while communication between layers is performed through service classes and repository contracts.

---

## Architectural Layers

```text
┌─────────────────────┐
│       FastAPI       │
├─────────────────────┤
│      Services       │
├─────────────────────┤
│ Repository Protocols│
├─────────────────────┤
│ Repository Impl.    │
├─────────────────────┤
│ PostgreSQL / Files  │
└─────────────────────┘
```

Dependencies always point toward abstractions rather than concrete implementations.

---

## Project Structure

```text
src/transit_advisor
├── api
├── domain
├── services
├── infrastructure
│   ├── archive
│   ├── database
│   └── repositories
└── tests
```

---

## Domain Layer

The domain layer contains business entities, validation logic and repository contracts.

Implemented entities:

```text
Agency
Route
Stop
Trip
StopTime
ScheduleVersion
ScheduleDiff
Subscription
Notification
```

Domain entities validate their own state and reject invalid data during creation.

Examples:

- route identifiers cannot be empty;
- agency identifiers must be valid;
- subscriptions require positive identifiers;
- notifications require non-empty messages;
- schedule differences cannot contain the same route in both added and removed collections.

---

## Repository Contracts

Repositories are defined as Protocol interfaces.

Implemented contracts:

```text
AgencyRepository
RouteRepository
StopRepository
TripRepository
StopTimeRepository
ScheduleVersionRepository
SubscriptionRepository
NotificationRepository
```

Application services depend on these contracts rather than infrastructure implementations.

Example:

```python
class NotificationService:
    def __init__(
        self,
        repository: NotificationRepository,
    ) -> None:
        self._repository = repository
```

---

## Service Layer

Services implement application use-cases and coordinate domain objects.

Implemented services:

```text
FeedValidator
ChecksumService
FeedUploadService
GtfsImportService
ScheduleVersionService
ScheduleDiffService
SubscriptionService
NotificationService
ScheduleUpdateService
```

### Responsibilities

| Service | Responsibility |
|----------|---------------|
| FeedValidator | GTFS archive validation |
| ChecksumService | SHA-256 checksum calculation |
| FeedUploadService | Feed import workflow |
| GtfsImportService | GTFS entity import |
| ScheduleVersionService | Schedule version management |
| ScheduleDiffService | Version comparison |
| SubscriptionService | Subscription management |
| NotificationService | Notification creation |
| ScheduleUpdateService | Processing schedule changes and generating notifications |

---

## Infrastructure Layer

The infrastructure layer contains implementations of repository contracts and external-data adapters.

### Database

Persistence is implemented using:

```text
PostgreSQL
SQLAlchemy ORM
```

Implemented repositories:

```text
SqlAlchemyAgencyRepository
SqlAlchemyRouteRepository
SqlAlchemyStopRepository
SqlAlchemyTripRepository
SqlAlchemyStopTimeRepository
SqlAlchemyScheduleVersionRepository
SqlAlchemySubscriptionRepository
SqlAlchemyNotificationRepository
```

### Archive Processing

GTFS archives are processed through:

```text
GtfsArchiveReader
```

The adapter reads ZIP archives incrementally and supports streaming processing of GTFS files.

This approach prevents loading the entire archive into memory and allows efficient processing of large transit datasets.

---

## Feed Processing Workflow

The feed ingestion process follows the sequence below.

```text
GTFS Archive
      │
      ▼
GtfsArchiveReader
      │
      ▼
FeedValidator
      │
      ▼
ChecksumService
      │
      ▼
FeedUploadService
      │
      ▼
ScheduleVersionService
      │
      ▼
GtfsImportService
      │
      ▼
PostgreSQL
```

---

## Schedule Change Processing

Schedule updates are processed by comparing route sets between schedule versions.

```text
Previous Schedule
        │
        ▼
ScheduleDiffService
        ▲
        │
Current Schedule
        │
        ▼
ScheduleDiff
        │
        ▼
ScheduleUpdateService
        │
        ▼
RouteRepository
        │
        ▼
SubscriptionRepository
        │
        ▼
NotificationService
        │
        ▼
NotificationRepository
```

Only subscribers affected by a route change receive notifications.

---

## API Layer

The presentation layer is implemented using FastAPI.

### Feed API

```text
POST /feeds
```

Responsibilities:

- upload GTFS archives;
- validate archive structure;
- calculate checksums;
- detect duplicate feeds;
- create schedule versions.

### Subscription API

```text
POST /subscriptions
GET  /subscriptions/users/{user_id}
```

Responsibilities:

- create subscriptions;
- prevent duplicate subscriptions;
- retrieve user subscriptions.

### Notification API

```text
GET /notifications/users/{user_id}
GET /notifications/users/{user_id}/unread
```

Responsibilities:

- retrieve user notifications;
- retrieve unread notifications.

---

## Error Handling

Validation and error handling are performed at multiple levels.

### Domain Layer

Domain entities validate incoming data and raise exceptions for invalid state.

Example:

```python
Route(
    agency_id=0,
    ...
)
```

results in:

```python
ValueError(
    "agency_id must be positive"
)
```

### Service Layer

Services enforce business rules.

Examples:

- duplicate feed uploads are rejected;
- duplicate subscriptions are prevented;
- invalid scheduling operations are ignored.

### Repository Layer

Database consistency is guaranteed by:

```text
Foreign Keys
Unique Constraints
Not Null Constraints
```

### API Layer

FastAPI converts application failures into HTTP responses.

Common responses:

```text
201 Created
200 OK
409 Conflict
422 Unprocessable Entity
```

---

## Testing Strategy

The project uses three testing levels.

### Unit Tests

Cover:

- domain entities;
- validation logic;
- business services.

### Integration Tests

Cover:

- repository implementations;
- PostgreSQL persistence;
- entity relationships.

### API Tests

Cover:

- request handling;
- dependency injection;
- endpoint behaviour;
- response formats.

---

## Key Architectural Decisions

### Clean Architecture

Business logic is isolated from external technologies.

The domain layer does not depend on:

- FastAPI;
- SQLAlchemy;
- PostgreSQL.

### Repository Pattern

Database access is centralized in repositories.

Benefits:

- separation of concerns;
- easier testing;
- interchangeable implementations.

### Streaming Processing

GTFS archives are processed incrementally.

Benefits:

- stable memory consumption;
- support for large datasets;
- improved scalability.

### Version-Based Change Detection

Each imported feed creates a schedule version.

Changes between versions are represented by:

```text
ScheduleDiff
```

which contains:

```text
added_routes
removed_routes
```

and serves as the basis for notification generation.

---

## Design Goals

The system was designed with the following goals:

- maintainability;
- separation of concerns;
- testability;
- scalability;
- support for large GTFS datasets;
- extensibility for future analytical features;
- efficient schedule change tracking;
- notification-based monitoring of transport updates.


## Future work

- comparison of timetable changes at Trip and StopTime levels, including departure time modifications and stop sequence changes.
