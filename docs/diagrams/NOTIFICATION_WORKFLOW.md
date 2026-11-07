# Notification Workflow

This diagram describes how route changes generate user notifications.

```mermaid
flowchart TD

    A[Previous Schedule]
        --> C[ScheduleDiffService]

    B[Current Schedule]
        --> C

    C --> D[ScheduleDiff]

    D --> E[ScheduleUpdateService]

    E --> F[RouteRepository]

    F --> G[SubscriptionRepository]

    G --> H[NotificationService]

    H --> I[NotificationRepository]

    I --> J[(PostgreSQL)]

    J --> K[Notification API]

    K --> L[Subscribed User]
```

## Description

1. Two schedule versions are compared.
2. `ScheduleDiffService` identifies route changes.
3. `ScheduleUpdateService` processes added and removed routes.
4. User subscriptions are retrieved.
5. `NotificationService` creates notifications for affected subscribers.
6. Notifications are saved in PostgreSQL.
7. Users retrieve notifications through the Notification API.
```
