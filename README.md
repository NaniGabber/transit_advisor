[![Docker Image CI](https://github.com/NaniGabber/transit_advisor/actions/workflows/docker-image.yml/badge.svg?branch=main)](https://github.com/NaniGabber/transit_advisor/actions/workflows/docker-image.yml)      [![CI](https://github.com/NaniGabber/transit_advisor/actions/workflows/ci.yml/badge.svg)](https://github.com/NaniGabber/transit_advisor/actions/workflows/ci.yml) ![Architecture](https://img.shields.io/badge/architecture-clean-brightgreen)

# Transit Advisor

Transit Advisor is an information system for processing and analyzing GTFS public transportation schedules. The project is designed for automated import of transit data, tracking schedule changes between versions, and notifying users about updates that interest them.

The core idea of the system is to transform raw GTFS feeds into structured data stored in a database and then detect differences between imported schedule versions.

## Architecture

The system follows the principles of Clean Architecture. Business logic is separated from infrastructure code, while interaction between layers is performed through protocols and services.

```text
src/transit_advisor
├── api
├── domain
├── services
├── infrastructure
│   ├── database
│   └── repositories
└── tests
```

The architecture boundaries are enforced automatically using `import-linter` (see `pyproject.toml`).

## Documentation

Additional project documentation is available in the `docs` directory.

| Document | Description |
|-----------|-------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture and architectural decisions |
| [docs/TESTING.md](docs/TESTING.md) | Testing strategy and test structure |
| [docs/REQUIREMENTS_TRACEABILITY.md](docs/REQUIREMENTS_TRACEABILITY.md) | Requirements traceability matrix |
| [docs/REFACTORING.md](docs/REFACTORING.md) | Architectural considerations and refactoring opportunities |
| [docs/diagrams/ER_DIAGRAM.md](docs/diagrams/ER_DIAGRAM.md) | Database ER diagram |
| [docs/diagrams/FEED_PROCESSING.md](docs/diagrams/FEED_PROCESSING.md) | GTFS feed import process |
| [docs/diagrams/NOTIFICATION_WORKFLOW.md](docs/diagrams/NOTIFICATION_WORKFLOW.md) | Notification generation workflow |
| [docs/API.md](docs/API.md) | API endpoint reference |

### Domain Layer

Contains domain entities and business rules:

- Agency
- Route
- Stop
- Trip
- StopTime
- ScheduleVersion
- ScheduleDiff
- Subscription
- Notification

### Service Layer

Contains application services that implement the core system use cases:

- GTFS data import (with rejected-row tracking);
- GTFS archive validation;
- SHA-256 checksum calculation;
- schedule version creation and management;
- schedule change detection (`ScheduleDiffService`);
- subscription and notification processing (`ScheduleUpdateService`);
- direct journey planning (`JourneyService`);
- route search, stop departure schedules, and analytics (`AnalyticsService`).

### Infrastructure Layer

Contains repository implementations and SQLAlchemy models for working with PostgreSQL.

---

## Current Project Status

At the current stage, the complete import cycle for the core GTFS entities has been implemented.

The system currently supports:

- importing `agency.txt`;
- importing `routes.txt`;
- importing `stops.txt`;
- importing `trips.txt` (linked to `schedule_version_id` and `service_id`);
- importing `stop_times.txt`;
- storing data in PostgreSQL;
- imported schedule versioning;
- duplicate import detection using SHA-256 checksums;
- rejected-row tracking during import (`ImportStats`);
- schedule version comparison at the route and stop-time levels;
- user subscriptions to routes;
- notification generation and persistence;
- direct journey planning between stops (no transfers);
- route search by number or stop;
- stop departure schedules;
- route schedule version comparison;
- analytics (trips by day, average headway, top stops);
- automatic notification creation when changes are detected;
- role-based access control (guest / user / admin);
- transaction management for feed import.

For each domain object, the following have been implemented:

- domain model;
- repository;
- integration tests;
- unit tests for business logic.

The project uses static type analysis with MyPy and automated testing with Pytest.

---

## GTFS Processing Pipeline

The current data processing workflow is as follows:

```text
GTFS Archive
        │
        ▼
Feed Validation
        │
        ▼
Checksum Calculation
        │
        ▼
Duplicate Detection
        │
        ▼
GTFS Import (versioned Trips)
        │
        ▼
Schedule Version Creation
        │
        ▼
ScheduleUpdateService (compare versions)
        │
        ▼
Notifications
```

## REST API

The following API endpoints are implemented.

### Feed API

```http
POST /feeds
```

Requires `X-Role: admin`. Returns `ImportStats` for each GTFS file.

### Route API

```http
GET /routes?q=&stop=&page=
GET /routes/{id}/diff?from_version=&to_version=
```

### Stop API

```http
GET /stops/{id}/departures?from=&page=&page_size=
```

### Journey API

```http
GET /journeys?from_stop=&to_stop=&page=&page_size=
```

Finds direct journeys (no transfers) between two stops.

### Analytics API

```http
GET /analytics/routes/{id}/trips-by-day
GET /analytics/routes/{id}/headway
GET /analytics/stops/top?limit=
```

### Subscription API

```http
POST /subscriptions
GET  /subscriptions/users/{user_id}
```

Requires `X-Role: user` or `X-Role: admin`.

### Notification API

```http
GET /notifications/users/{user_id}
GET /notifications/users/{user_id}/unread
```

### Authentication & Roles

The API uses a simple `X-Role` header (for course project purposes):

- `guest` (default) — read-only access.
- `user` — can create subscriptions and view notifications.
- `admin` — can upload GTFS feeds.

---

## Testing

The project contains three testing levels.

### Unit Tests

Verify:

- domain entities;
- business rules;
- services (`ScheduleDiffService`, `ScheduleUpdateService`, `JourneyService`);
- GTFS import process (including `ImportStats`);
- schedule versioning.

### Integration Tests

Verify:

- SQLAlchemy repositories (including `search`, `find_departures`, `find_direct_journeys`);
- PostgreSQL integration;
- correctness of entity relationships;
- data persistence and retrieval;
- database isolation between tests (via SAVEPOINT).

### API Tests

Verify:

- Feed API;
- Route API (search and version comparison);
- Stop API (departure schedules);
- Journey API;
- Analytics API;
- Subscription API;
- Notification API;
- role-based access control;
- correct HTTP responses;
- dependency injection configuration.

## Logging

At the current stage, centralized logging has not yet been implemented.

During development and testing, the project relies on:

- Python exceptions;
- SQLAlchemy logs and messages;
- PostgreSQL messages;
- FastAPI logs and messages;
- Pytest reports.

Future versions are expected to introduce structured logging based on Python's standard `logging` module for monitoring feed imports, error handling, and system operation auditing.

Run tests:

```bash
pytest
```

Type checking:

```bash
mypy src tests
```

Architecture checks:

```bash
lint-imports
```

---

## Technology Stack

- Python 3.13
- PostgreSQL
- SQLAlchemy
- Psycopg
- FastAPI
- Pydantic
- Pytest
- MyPy
- Ruff
- import-linter
- Docker

---

## Future Development

The current implementation provides the foundation for a transit schedule change monitoring service.

Future development may include:

- email notifications for users;
- structured logging and monitoring;
- support for multiple transit operators;
- a web interface for viewing schedules and change history;
- advanced analytics (peak-hour intervals, route popularity).

## Author

Course project developed as part of the Python Programming course.

**Author:** Alexandr Pogrebnyuk

### Jira

```text
https://nanilennauchpage.atlassian.net/jira/software/projects/TA
```
