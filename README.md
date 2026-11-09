[![Docker Image CI](https://github.com/NaniGabber/transit_advisor/actions/workflows/docker-image.yml/badge.svg?branch=main)](https://github.com/NaniGabber/transit_advisor/actions/workflows/docker-image.yml)
[![CI](https://github.com/NaniGabber/transit_advisor/actions/workflows/ci.yml/badge.svg)](https://github.com/NaniGabber/transit_advisor/actions/workflows/ci.yml)

---

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

- GTFS data import;
- GTFS archive validation;
- SHA-256 checksum calculation;
- schedule version creation and management;
- schedule change detection (`ScheduleDiffService`);
- subscription and notification processing (`ScheduleUpdateService`);
- route search and stop departure schedules.

### Infrastructure Layer

Contains repository implementations and SQLAlchemy models for working with PostgreSQL.

---

## Current Project Status

At the current stage, the complete import cycle for the core GTFS entities has been implemented.

The system currently supports:

- importing `agency.txt`;
- importing `routes.txt`;
- importing `stops.txt`;
- importing `trips.txt` (linked to `schedule_version_id`);
- importing `stop_times.txt`;
- storing data in PostgreSQL;
- imported schedule versioning;
- duplicate import detection using SHA-256 checksums;
- schedule version comparison at the route and stop-time levels;
- user subscriptions to routes;
- notification generation and persistence;
- API for GTFS feed import;
- API for subscription management;
- API for notification retrieval;
- API for route search;
- API for stop departure schedules;
- API for route schedule version comparison;
- automatic notification creation when changes are detected.

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

### Route API

```http
GET /routes?q=&stop=&page=
GET /routes/{id}/diff?from_version=&to_version=
```

### Stop API

```http
GET /stops/{id}/departures?from=&page=&page_size=
```

### Subscription API

```http
POST /subscriptions
GET  /subscriptions/users/{user_id}
```

### Notification API

```http
GET /notifications/users/{user_id}
GET /notifications/users/{user_id}/unread
```

---

## Testing

The project contains three testing levels.

### Unit Tests

Verify:

- domain entities;
- business rules;
- services (`ScheduleDiffService`, `ScheduleUpdateService`);
- GTFS import process;
- schedule versioning.

### Integration Tests

Verify:

- SQLAlchemy repositories (including `search` and `find_departures`);
- PostgreSQL integration;
- correctness of entity relationships;
- data persistence and retrieval;
- database isolation between tests (via SAVEPOINT).

### API Tests

Verify:

- Feed API;
- Route API (search and version comparison);
- Stop API (departure schedules);
- Subscription API;
- Notification API;
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
- Docker

---

## Future Development

The current implementation provides the foundation for a transit schedule change monitoring service.

Futureiple transit operators;
- a web interface for viewing schedules and change history.

---

## Author

Course project developed as part of the Python Programming course.

**Author:** Alexandr Pogrebnyuk

### Jira

```text
https://nanilennauchpage.atlassian.net/jira/software/projects/TA
```
