# API Reference

Цей документ описує REST API сервісу Transit Advisor.

## Base URL

```text
http://localhost:8000
```

## Формати

- Усі запити та відповіді використовують `application/json`, окрім завантаження файлів (`multipart/form-data`).
- Час у полях `arrival_time` та `departure_time` передається у форматі `HH:MM:SS` (GTFS).
- Дати (наприклад, `created_at`) передаються у форматі ISO 8601.

---

## Feed API

### `POST /feeds`

Завантаження GTFS-архіву.

**Request body:**

`multipart/form-data` з полем `file` (ZIP-архів).

**Response (201 Created):**

```json
{
  "checksum": "a1b2c3d4e5f6...",
  "imported": true,
  "duplicate": false
}
```

**Errors:**

- `422 Unprocessable Entity` — файл не є ZIP-архівом або не містить обов'язкових GTFS-файлів.
- `409 Conflict` — архів із таким самим `checksum` уже імпортовано.

---

## Route API

### `GET /routes`

Пошук маршрутів за номером, назвою або зупинкою.

**Query parameters:**

| Параметр | Тип | Обов'язковий | Опис |
|----------|-----|--------------|------|
| `q` | string | Ні | Пошук за `route_id`, `short_name` або `long_name`. |
| `stop` | integer | Ні | Фільтр за внутрішнім ID зупинки. |
| `page` | integer | Ні | Номер сторінки (за замовчуванням `1`). |
| `page_size` | integer | Ні | Кількість елементів на сторінці (за замовчуванням `20`, максимум `100`). |

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

Порівняння двох версій розкладу для конкретного маршруту.

**Path parameters:**

| Параметр | Тип | Опис |
|----------|-----|------|
| `route_id` | integer | Внутрішній ID маршруту. |

**Query parameters:**

| Параметр | Тип | Обов'язковий | Опис |
|----------|-----|--------------|------|
| `from_version` | integer | Так | ID початкової версії розкладу. |
| `to_version` | integer | Так | ID кінцевої версії розкладу. |

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

- `404 Not Found` — маршрут не знайдено.

---

## Stop API

### `GET /stops/{stop_id}/departures`

Розклад відправлень за зупинкою.

**Path parameters:**

| Параметр | Тип | Опис |
|----------|-----|------|
| `stop_id` | integer | Внутрішній ID зупинки. |

**Query parameters:**

| Параметр | Тип | Обов'язковий | Опис |
|----------|-----|--------------|------|
| `from` | string | Ні | Час у форматі `HH:MM` (за замовчуванням — поточний). |
| `page` | integer | Ні | Номер сторінки (за замовчуванням `1`). |
| `page_size` | integer | Ні | Кількість елементів на сторінці (за замовчуванням `20`, максимум `100`). |

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

- `422 Unprocessable Entity` — некоректний формат часу (не `HH:MM`).

---

## Subscription API

### `POST /subscriptions`

Створення підписки на маршрут.

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

- `409 Conflict` — підписка вже існує.
- `422 Unprocessable Entity` — некоректний payload.

### `GET /subscriptions/users/{user_id}`

Отримання підписок користувача.

**Path parameters:**

| Параметр | Тип | Опис |
|----------|-----|------|
| `user_id` | integer | ID користувача. |

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

Отримання всіх сповіщень користувача.

**Path parameters:**

| Параметр | Тип | Опис |
|----------|-----|------|
| `user_id` | integer | ID користувача. |

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

Отримання непрочитаних сповіщень користувача.

**Path parameters:**

| Параметр | Тип | Опис |
|----------|-----|------|
| `user_id` | integer | ID користувача. |

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

## Загальні коди помилок

| Код | Опис |
|-----|------|
| `400 Bad Request` | Некоректний запит (наприклад, відсутні обов'язкові поля). |
| `404 Not Found` | Ресурс не знайдено (наприклад, маршрут або користувач). |
| `409 Conflict` | Конфлікт (наприклад, дублікат підписки або фіду). |
| `422 Unprocessable Entity` | Помилка валідації (наприклад, некоректний формат часу або відсутні GTFS-файли). |
| `500 Internal Server Error` | Внутрішня помилка сервера. |
