# Refactoring Notes

## Purpose

This document records architectural limitations identified during development and possible directions for future refactoring.

---

## Schedule Version Integration

### Current State

The system stores schedule versions separately from transport entities.

Current entities:

- Agency
- Route
- Stop
- Trip
- StopTime

are not directly linked to:

- ScheduleVersion

As a result, imported transport data represents only the latest known state.

### Limitation

The application cannot reconstruct a complete historical snapshot of a schedule version.

For example:

```text
Schedule Version #1
Route 11

Schedule Version #2
Route 11
```

are currently represented by the same database records.

### Future Refactoring

Introduce:

```text
schedule_version_id
```

into:

- Agency
- Route
- Stop
- Trip
- StopTime

This would allow storing complete historical versions and comparing them directly.

---

## Route Comparison

### Current State

ScheduleDiffService compares route sets and detects:

- added routes;
- removed routes.

### Limitation

The implementation does not compare:

- stop sequences;
- departure times;
- trip definitions.

### Future Refactoring

Extend comparison logic to operate on:

```text
Trip
StopTime
```

and detect timetable-level modifications.

Examples:

- departure time changed;
- stop added to route;
- stop removed from route.

---

## Feed Import Transactions

### Current State

Repositories perform commits independently.

Example:

```python
repository.save(...)
```

immediately commits data.

### Limitation

A failure during import may leave partially imported data inside the database.

### Future Refactoring

Use a Unit of Work pattern or application-level transactions for the complete import process.

Benefits:

- atomic imports;
- consistent rollback behaviour;
- simplified error recovery.

---

## Logging

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

---

## Analytics

### Current State

Analytical reports are not implemented.

### Future Refactoring

Add:

- route frequency statistics;
- peak-hour interval analysis;
- busiest stops;
- route popularity metrics.

---

## Conclusion

The current implementation prioritizes correctness, maintainability and extensibility.

Future refactoring efforts should focus primarily on:

1. Full schedule version support.
2. Timetable-level change detection.
3. Transaction management.
4. Structured logging.
5. Analytical features.
