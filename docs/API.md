# API Reference

This document describes the REST API of the Transit Advisor service.

## Base URL

```text
http://localhost:8000
```

## Formats

- All requests and responses use `application/json`, except for file uploads, which use `multipart/form-data`.
- Time values in the `arrival_time` and `departure_time` fields are provided in `HH:MM:SS` format (GTFS).
- Dates (for example, `created_at`) are provided in ISO 8601 format.

## Authentication & Roles

The API uses a simple `X-Role` header (for course project purposes):

| Role | Description |
|------|-------------|
| `guest` (default) | Read-only access: search routes, view departures, compare versions, view analytics. |
| `user` | Can create subscriptions and view notifications. |
| `admin` | Can upload GTFS feeds and create subscriptions. |

Example:

```bash
curl -X POST http://localhost:8000/feeds \
  -H "X-Role: admin" \
  -F "file=@feed.zip"
```

If the header is missing, the role defaults to `guest`.

---

## Feed API

### `POST /feeds`

Uploads a GTFS archive. **Requires `X-Role: admin`.**

**Request body:**

`multipart/form-data` with a `file` field (ZIP archive).

**Response (201 Created):**

```json
{
  "checksum": "a1b2c3d4e5f6...",
  "imported": true,
  "duplicate": false,
  "stats": {
    "agencies": {"imported": 1, "rejected": 0},
    "routes": {"imported": 10, "rejected": 2},
    "stops": {"imported": 50, "rejected": 0},
    "trips": {"imported": 20, "rejected": 1},
    "stop_times": {"imported": 100, "rejected": 3}
  }
}
```

**Errors:**

- `403 Forbidden` — role is not `admin`.
- `422 Unprocessable Entity` — the file is not a ZIP archive or does not contain the required GTFS files.
- `409 Conflict` — an archive with the same `checksum` has already been imported.

---

## Route API

### `GET /routes`

Searches routes by route number, name, or stop.

**Query parameters:**

| Parameter | Type | Required | Description |
|------------|------|----------|-------------|
| `q` | string | No | Search by `route_id`, `short_name`, or `long_name`. |
| `stop` | integer | No | Filter by internal stop ID. |
| `page` | integer | No | Page number (default: `1`). |
| `page_size` | integer | No | Number of items per page (default: `20`, maximum: `100`). |

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "agency_id": 1,
    "route_id": "15",
    "short_name": "15",
    "long_name": "Center",
    "route_type": 3
  }
]
```

### `GET /routes/{route_id}/diff`

Compares two schedule versions for a specific route.

**Path parameters:**

| Parameter | Type | Description |
|------------|------|-------------|
| `route_id` | integer | Internal route ID. |

**Query parameters:**

| Parameter | Type | Required | Description |
|------------|------|----------|-------------|
| `from_version` | integer | Yes | Source schedule version ID. |
| `to_version` | integer | Yes | Target schedule version ID. |

**Response (200 OK):**

```json
{
  "from_version": 1,
  "to_version": 2,
  "added_routes": [],
  "removed_routes": [],
  "changed_stop_times": {
    "15": [1, 2]
  }
}
```

**Errors:**

- `404 Not Found` — route not found.

---

## Stop API

### `GET /stops/{stop_id}/departures`

Returns departure schedules for a stop.

**Path parameters:**

| Parameter | Type | Description |
|------------|------|-------------|
| `stop_id` | integer | Internal stop ID. |

**Query parameters:**

| Parameter | Type | Required | Description |
|------------|------|----------|-------------|
| `from` | string | No | Time in `HH:MM` format (defaults to the current time). |
| `page` | integer | No | Page number (default: `1`). |
| `page_size` | integer | No | Number of items per page (default: `20`, maximum: `100`). |

**Response (200 OK):**

```json
[
  {
    "trip_id": 1,
    "stop_id": 1,
    "arrival_time": "08:00:00",
    "departure_time": "08:01:00",
    "stop_sequence": 1
  }
]
```

**Errors:**

- `422 Unprocessable Entity` — invalid time format (must be `HH:MM`).

---

## Journey API

### `GET /journeys`

Finds direct journeys (no transfers) between two stops.

**Query parameters:**

| Parameter | Type | Required | Description |
|------------|------|----------|-------------|
| `from_stop` | integer | Yes | Internal ID of the departure stop. |
| `to_stop` | integer | Yes | Internal ID of the arrival stop. |
| `page` | integer | No | Page number (default: `1`). |
| `page_size` | integer | No | Number of items per page (default: `20`, maximum: `100`). |

**Response (200 OK):**

```json
[
  {
    "trip_id": 1,
    "from_stop_id": 1,
    "to_stop_id": 2,
    "departure_time": "08:00:00",
    "arrival_time": "08:10:00",
    "stop_sequence_start": 1,
    "stop_sequence_end": 2
  }
]
```

**Errors:**

- `422 Unprocessable Entity` — missing or invalid `from_stop` / `to_stop`.

---

## Analytics API

### `GET /analytics/routes/{route_id}/trips-by-day`

Returns the number of trips for a route grouped by `service_id` (current schedule version).

**Path parameters:**

| Parameter | Type | Description |
|------------|------|-------------|
| `route_id` | integer | Internal route ID. |

**Response (200 OK):**

```json
{
  "route_id": 1,
  "trips_by_day": {
    "WEEKDAY": 120,
    "SATURDAY": 60,
    "SUNDAY": 40
  }
}
```

### `GET /analytics/routes/{route_id}/headway`

Returns the average headway (in minutes) between departures for a route.

**Path parameters:**

| Parameter | Type | Description |
|------------|------|-------------|
| `route_id` | integer | Internal route ID. |

**Response (200 OK):**

```json
{
  "route_id": 1,
  "average_headway_minutes": 10.5
}
```

If there are fewer than two departures, `average_headway_minutes` is `null`.

### `GET /analytics/stops/top`

Returns the top stops by number of distinct routes.

**Query parameters:**

| Parameter | Type | Required | Description |
|------------|------|----------|-------------|
| `limit` | integer | No | Number of stops to return (default: `10`, maximum: `100`). |

**Response (200 OK):**

```json
{
  "stops": [
    {"stop_id": 1, "route_count": 5},
    {"stop_id": 2, "route_count": 4}
  ]
}
```

---

## Subscription API

### `POST /subscriptions`

Creates a route subscription. **Requires `X-Role: user` or `X-Role: admin`.**

**Request body:**

```json
{
  "user_id": 1,
  "route_id": 1
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "user_id": 1,
  "route_id": 1,
  "is_active": true
}
```

**Errors:**

- `403 Forbidden` — role is not `user` or `admin`.
- `409 Conflict` — subscription already exists.
- `422 Unprocessable Entity` — invalid payload.

### `GET /subscriptions/users/{user_id}`

Returns all subscriptions for a user.

**Path parameters:**

| Parameter | Type | Description |
|------------|------|-------------|
| `user_id` | integer | User ID. |

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "user_id": 1,
    "route_id": 1,
    "is_active": true
  }
]
```

---

## Notification API

### `GET /notifications/users/{user_id}`

Returns all notifications for a user.

**Path parameters:**

| Parameter | Type | Description |
|------------|------|-------------|
| `user_id` | integer | User ID. |

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "user_id": 1,
    "subscription_id": 1,
    "schedule_version_id": 1,
    "message": "Schedule for route 15 has changed",
    "created_at": "2026-11-01T12:00:00Z",
    "is_read": false
  }
]
```

### `GET /notifications/users/{user_id}/unread`

Returns all unread notifications for a user.

**Path parameters:**

| Parameter | Type | Description |
|------------|------|-------------|
| `user_id` | integer | User ID. |

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "user_id": 1,
    "subscription_id": 1,
    "schedule_version_id": 1,
    "message": "Schedule for route 15 has changed",
    "created_at": "2026-11-01T12:00:00Z",
    "is_read": false
  }
]
```

---

## Common Error Codes

| Code | Description |
|------|-------------|
| `400 Bad Request` | Invalid request (for example, invalid `X-Role` value). |
| `403 Forbidden` | Role is not allowed to access this endpoint. |
| `404 Not Found` | Resource not found (for example, route or user). |
| `409 Conflict` | Conflict (for example, duplicate subscription or feed). |
| `422 Unprocessable Entity` | Validation error (for example, invalid time format or missing GTFS files). |
| `500 Internal Server Error` | Internal server error. |
