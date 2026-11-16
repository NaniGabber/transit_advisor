# Refactoring Notes

## Purpose

This document records architectural limitations identified during development and possible directions for future refactoring.

Status legend:

- **DONE** — implemented and covered by tests.
- **PARTIAL** — partially implemented; remaining work is described.
- **PLANNED** — not implemented; intended for future work.
- **DEFERRED** — consciously postponed; rationale is given.

---

## Schedule Version Integration

### Status: PARTIAL

### Current State

The system stores schedule versions separately from transport entities.

Current entities:

- Agency
- Route
- Stop
- Trip
- StopTime
- ScheduleVersion

`Trip` is linked to `ScheduleVersion` via `Trip.schedule_version_id` and `Trip.service_id`.
`StopTime` inherits the version through `Trip`.
`Agency`, `Route`, and `Stop` remain reference data.

`Trip.trip_id` is unique **per schedule version** (`uq_trip_version`), not globally.

### Limitation

The application cannot reconstruct a complete historical snapshot of
`Agency`, `Route`, and `Stop` for a given schedule version.

For example:

```text
Schedule Version #1
Route 11

Schedule Version #2
Route 11
```

are still represented by the same `Route` record. `Trip` and `StopTime`,
however, are versioned.

### Future Refactoring

If full historical snapshots of reference data are required, introduce:

```text
schedule_version_id
```

into:

- Agency
- Route
- Stop

See ADR-002 for the decision to keep them as reference data.

---

## Route Comparison

### Status: DONE

### Current State

`ScheduleDiffService` compares route sets and detects:

- added routes;
- removed routes;
- changed stop times (arrival/departure).

Two paths are available:

- `compare_routes(...)` — by surrogate `Trip.id` (used by `process_update`);
- `compare_versions(...)` — by GTFS `trip_id` (used by `process_version_update`
  and `compare_route_versions`).

### Limitation

None for the current scope. The GTFS `trip_id` is assumed stable between
versions of the same feed.

### Future Refactoring

If `trip_id` stops being stable (e.g. cross-agency comparison), introduce a
stable domain-level trip identifier.

---

## Feed Import Transactions

### Status: DONE

### Current State

Repositories use `flush()` instead of `commit()` in `save()` methods.

`POST /feeds` wraps the entire import in `with session.begin()`, ensuring that
a failure rolls back all changes (version creation, import, and notifications).

### Limitation

None for the current scope.

### Future Refactoring

If more complex workflows are added, consider a Unit of Work pattern to
centralize transaction boundaries.

---

## Logging

### Status: PLANNED

### Current State

The system relies on:

- FastAPI exception handling;
- SQLAlchemy exceptions;
- PostgreSQL error messages;
- Pytest reports.

### Limitation

Operational events are not recorded centrally.

### Future Refactoring

Implement structured logging using:

```python
logging
```

for:

- feed imports;
- validation failures;
- schedule updates;
- notification creation;
- critical application errors.

---

## User Management

### Status: PARTIAL

### Current State

Subscriptions are associated with a numeric user identifier.

Role-based access control is implemented via the `X-Role` header (`guest`, `user`, `admin`).

### Limitation

Authentication and authorization are not implemented (no JWT, no passwords).

### Future Refactoring

Introduce:

- User entity;
- Authentication (JWT or OAuth2);
- Authorization policies.

Out of scope for the current iteration; the numeric `user_id` and `X-Role` header are sufficient
for subscription and notification flows.

---

## Analytics

### Status: DONE

### Current State

The following analytical endpoints are implemented:

- `GET /analytics/routes/{id}/trips-by-day` — trips grouped by `service_id`.
- `GET /analytics/routes/{id}/headway` — average headway in minutes.
- `GET /analytics/stops/top` — top stops by number of routes.

### Limitation

Analytics are computed for the **latest** schedule version only.

### Future Refactoring

Add support for querying analytics for a specific `version_id` (e.g. `?version_id=2`).

---

## GTFS Import Optimization

### Status: PLANNED

### Current State

Current implementation performs repository lookups for each imported row.

Example:

- `find_by_trip_id(...)`
- `find_by_stop_id(...)`

This approach keeps memory consumption constant but generates a significant number of database queries for large GTFS datasets.

### Future Refactoring

Future optimization may include:

- caching trip identifiers;
- caching stop identifiers;
- batch inserts;
- bulk SQLAlchemy operations.

This would significantly improve import performance for feeds containing millions of StopTime records.

---

## Test Database Isolation

### Status: PARTIAL

### Current State

Integration tests use a shared PostgreSQL instance.

The `session` fixture uses `SAVEPOINT` transactions to roll back changes after
each test, preventing data from leaking between tests.

### Limitation

`Base.metadata.create_all` / `drop_all` may still be slow for large schemas.

### Future Refactoring

Consider using a dedicated test database or `pytest-postgresql` plugin for
faster isolation.

---

## API Search and Pagination

### Status: DONE

### Current State

- `GET /routes` supports `q` (query), `stop` (stop filter), `page`, `page_size`.
- `GET /stops/{id}/departures` supports `from` (time filter), `page`, `page_size`.
- `GET /routes/{id}/diff` supports `from_version`, `to_version`.
- `GET /journeys` supports `from_stop`, `to_stop`, `page`, `page_size`.

### Limitation

Pagination is offset-based, which may become slow for very large datasets.

### Future Refactoring

Switch to cursor-based pagination (keyset pagination) for large tables.

---

## Architecture Enforcement

### Status: DONE

### Current State

`import-linter` contracts are defined in `pyproject.toml` to enforce Clean Architecture boundaries:

- `api` → `services` → `domain`
- `domain` must not import `infrastructure`, `api`, or `services`.
- `services` must not import `api`.
- `infrastructure` must not import `api`.

### Limitation

None for the current scope.

### Future Refactoring

If new layers are added (e.g. `application`), update the contracts accordingly.

---

## Conclusion

The current implementation prioritizes correctness, maintainability and extensibility.

Future refactoring efforts should focus primarily on:

1. Full schedule version support (**PARTIAL** — `Trip`/`StopTime` done,
   `Route`/`Stop`/`Agency` deferred, see ADR-002).
2. Timetable-level change detection (**DONE** — by GTFS `trip_id`).
3. Transaction management (**DONE** — `session.begin()` in `POST /feeds`).
4. Structured logging (**PLANNED**).
5. Analytical features (**DONE** — trips-by-day, headway, top stops).
6. Test database isolation (**PARTIAL** — SAVEPOINT used, but `create_all`
   still slow).
7. API search and pagination (**DONE** — offset-based, cursor-based planned).
8. Architecture enforcement (**DONE** — `import-linter`).
9. Authentication and authorization (**PARTIAL** — `X-Role` header, no JWT).
