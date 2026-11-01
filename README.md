[![Docker Image CI](https://github.com/NaniGabber/transit_advisor/actions/workflows/docker-image.yml/badge.svg?branch=main)](https://github.com/NaniGabber/transit_advisor/actions/workflows/docker-image.yml)      [![CI](https://github.com/NaniGabber/transit_advisor/actions/workflows/ci.yml/badge.svg)](https://github.com/NaniGabber/transit_advisor/actions/workflows/ci.yml)
# transit_advisor
Course project VII term

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

### Domain Layer

Містить доменні сутності та бізнес-правила:

- Agency
- Route
- Stop
- Trip
- StopTime
- ScheduleVersion
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

---

## Testing

Проєкт містить два рівні тестування:

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

- повноцінний REST API для керування підписками;
- розширення механізму порівняння версій розкладу;
- автоматичне формування сповіщень на основі виявлених змін;
- email-повідомлення користувачам;
- підтримку декількох транспортних операторів;
- розширену аналітику змін транспортної мережі;
- веб-інтерфейс для перегляду розкладів та історії змін.

---

## Author

Course project developed as part of the Python Programming course.

**Author:** AlexandrPogrebnyuk



Jira:
```bash
https://nanilennauchpage.atlassian.net/jira/software/projects/TA
```
