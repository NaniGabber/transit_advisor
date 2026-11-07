[![Docker Image CI](https://github.com/NaniGabber/transit_advisor/actions/workflows/docker-image.yml/badge.svg?branch=main)](https://github.com/NaniGabber/transit_advisor/actions/workflows/docker-image.yml)      [![CI](https://github.com/NaniGabber/transit_advisor/actions/workflows/ci.yml/badge.svg)](https://github.com/NaniGabber/transit_advisor/actions/workflows/ci.yml)

___
# Transit Advisor

Transit Advisor — це інформаційна система для обробки та аналізу GTFS-розкладів громадського транспорту. Проєкт призначений для автоматизованого імпорту транспортних даних, відстеження змін між версіями розкладів та інформування користувачів про зміни, які їх цікавлять.

Основна ідея системи полягає у перетворенні сирих GTFS-фідів на структуровані дані, збережені у базі даних, та подальшому виявленні відмінностей між завантаженими версіями розкладів.

## Архітектура

Система побудована відповідно до принципів Clean Architecture. Бізнес-логіка відокремлена від інфраструктурного коду, а взаємодія між шарами виконується через протоколи та сервіси.

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

## Документація

Додаткова документація проєкту доступна в каталозі `docs`.

| Документ | Опис |
|-----------|-------------|
| docs/ARCHITECTURE.md | Архітектура системи та прийняті архітектурні рішення |
| docs/TESTING.md | Стратегія тестування та структура тестів |
| docs/REQUIREMENTS_TRACEABILITY.md | Відповідність вимог реалізації |
| docs/REFACTORING.md | Опис архітектурних особливостий та шляхів рефакторингу |d
| docs/diagrams/ER_DIAGRAM.md | ER-діаграма бази даних |
| docs/diagrams/FEED_PROCESSING.md | Процес імпорту GTFS-фідів |
| docs/diagrams/NOTIFICATION_WORKFLOW.md | Процес створення сповіщень |

### Domain Layer

Містить доменні сутності та бізнес-правила:

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

Містить прикладні сервіси, що реалізують основні сценарії системи:

- імпорт GTFS-даних;
- валідацію GTFS-архівів;
- обчислення SHA-256 контрольних сум;
- створення та керування версіями розкладів;
- виявлення змін між версіями;
- обробку підписок та сповіщень.

### Infrastructure Layer

Містить реалізації репозиторіїв та моделі SQLAlchemy для роботи з PostgreSQL.

---

## Поточний стан проєкту

На даному етапі реалізовано повний цикл імпорту основних GTFS-сутностей.

Система підтримує:

- імпорт agency.txt;
- імпорт routes.txt;
- імпорт stops.txt;
- імпорт trips.txt;
- імпорт stop_times.txt;
- збереження даних у PostgreSQL;
- версіонування імпортованих розкладів;
- визначення дублікатів імпорту за SHA-256 checksum;
- порівняння версій розкладу на рівні маршрутів;
- підписки користувачів на маршрути;
- створення та збереження сповіщень.
- API для імпорту GTFS-фідів;
- API для керування підписками;
- API для отримання сповіщень;
- автоматичне створення сповіщень при виявленні змін.

Для кожного доменного об'єкта реалізовані:

- доменна модель;
- репозиторій;
- інтеграційні тести;
- unit-тести бізнес-логіки.

Проєкт використовує статичний аналіз типів через MyPy та автоматизоване тестування через Pytest.

---

## GTFS Processing Pipeline

Поточний процес обробки даних виглядає таким чином:

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
GTFS Import
        │
        ▼
Schedule Version Creation
        │
        ▼
Schedule Change Detection
        │
        ▼
Notifications
```

## REST API

Реалізовані такі API-ендпоїнти.

### Feed API

```http
POST /feeds\
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

Проєкт містить три рівні тестування:

### Unit Tests

Перевіряють:

- доменні сутності;
- бізнес-правила;
- сервіси;
- GTFS-імпорт;
- версіонування розкладів.

### Integration Tests

Перевіряють:

- SQLAlchemy репозиторії;
- роботу з PostgreSQL;
- коректність зв'язків між сутностями;
- збереження та пошук даних.

### API Tests

Перевіряють:

- Feed API;
- Subscription API;
- Notification API;
- коректність HTTP-відповідей;
- dependency injection.

## Logging

На поточному етапі централізоване логування не реалізовано.

Під час розробки та тестування використовуються:

- винятки Python;
- повідомлення SQLAlchemy;
- повідомлення PostgreSQL;
- повідомлення FastAPI;
- звіти Pytest.

У майбутніх версіях планується реалізація структурованого логування на базі стандартного модуля `logging` для моніторингу імпорту фідів, обробки помилок та аудиту операцій системи.

Запуск тестів:

```bash
pytest
```

Перевірка типізації:

```bash
mypy src tests
```

---

## Використані технології

- Python 3.13
- PostgreSQL
- SQLAlchemy
- Psycopg
- Pytest
- MyPy
- Ruff
- Docker

---

## Вектор подальшого розвитку

Поточна реалізація формує основу для сервісу моніторингу змін транспортних розкладів.

Подальший розвиток системи передбачає:

- пошук маршрутів за номером та зупинкою;
- формування розкладу за конкретною зупинкою;
- розширення механізму порівняння версій розкладу;
- email-повідомлення користувачам;
- централізоване логування та моніторинг;
- аналітичні звіти щодо транспортної мережі;
- підтримку декількох транспортних операторів;
- веб-інтерфейс для перегляду розкладів та історії змін.

---

## Author

Course project developed as part of the Python Programming course.

**Author:** AlexandrPogrebnyuk



Jira:
```bash
https://nanilennauchpage.atlassian.net/jira/software/projects/TA
```
