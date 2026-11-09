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

---

## Feed API

### `POST /feeds`

Uploads a GTFS archive.

**Request body:**

`multipart/form-data` with a `file` field (ZIP archive).

**Response (201 Created):**

```json
{
  "checksum": "a1b2c3d4e5f6...",
  "imported": true,
  "duplicate": false
}
```

**Errors:**

- `422 Unprocessable Entity` – the file is not a ZIP archive or does not contain the required GTFS files.
- `409 Conflict` – an archive with the same `checksum` has already been imported.

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

- `404 Not Found` – route not found.

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

- `422 Unprocessable Entity` – invalid time format (must be `HH:MM`).

---

## Subscription API

### `POST /subscriptions`

Creates a route subscription.

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

- `409 Conflict` – subscription already exists.
- `422 Unprocessable Entity` – invalid payload.

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
| `400 Bad Request` | Invalid request (for example, missing required fields). |
| `404 Not Found` | Resource not found (for example, route or user). |
| `409 Conflict` | Conflict (for example, duplicate subscription or feed). |
| `422 Unprocessable Entity` | Validation error (for example, invalid time format or missing GTFS files). |
| `500 Internal Server Error` | Internal server error. |
