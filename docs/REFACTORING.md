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

`Trip` is linked to `ScheduleVersion` via `Trip.schedule_version_id`.
`StopTime` inherits the version through `Trip`.
`Agency`, `Route`, and `Stop` remain reference data.

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
- changed stop times (arrival/departure);
- added stops;
- removed stops.

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

### Status: PARTIAL

### Current State

Repositories use `flush()` instead of `commit()` in `save()` methods.

`FeedUploadService.upload(...)` does not yet wrap "create version + import +
process update" in a single transaction.

### Limitation

A failure during import may leave partially imported data inside the database
if the service does not roll back.

### Future Refactoring

Use a Unit of Work pattern or application-level transactions for the complete
import process.

Benefits:

- atomic imports;
- consistent rollback behaviour;
- simplified error recovery.

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

### Status: DEFERRED

### Current State

Subscriptions are associated with a numeric user identifier.

### Limitation

Authentication and authorization are not implemented.

### Future Refactoring

Introduce:

- User entity;
- Roles;
- Authentication;
- Authorization policies.

Out of scope for the current iteration; the numeric `user_id` is sufficient
for subscription and notification flows.

---

## Analytics

### Status: PLANNED

### Current State

Analytical reports are not implemented.

### Future Refactoring

Add:

- route frequency statistics by day of week;
- peak-hour interval analysis;
- busiest stops;
- route popularity metrics.

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

### Limitation

Pagination is offset-based, which may become slow for very large datasets.

### Future Refactoring

Switch to cursor-based pagination (keyset pagination) for large tables.

---

## Conclusion

The current implementation prioritizes correctness, maintainability and extensibility.

Future refactoring efforts should focus primarily on:

1. Full schedule version support (**PARTIAL** — `Trip`/`StopTime` done,
   `Route`/`Stop`/`Agency` deferred, see ADR-002).
2. Timetable-level change detection (**DONE** — by GTFS `trip_id`).
3. Transaction management (**PARTIAL** — `flush()` in repositories,
   application-level transaction pending).
4. Structured logging (**PLANNED**).
5. Analytical features (**PLANNED**).
6. Test database isolation (**PARTIAL** — SAVEPOINT used, but `create_all`
   still slow).
7. API search and pagination (**DONE** — offset-based, cursor-based planned).
