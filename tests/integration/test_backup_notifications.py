import psycopg
from sqlalchemy import Engine, text


def test_committed_database_change_notifies_backup_worker(engine: Engine) -> None:
    connection_string = engine.url.set(drivername="postgresql").render_as_string(
        hide_password=False
    )
    with psycopg.connect(connection_string, autocommit=True) as listener:
        listener.execute("LISTEN transit_advisor_backup")

        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO schedule_versions (checksum, imported_at) "
                    "VALUES (:checksum, now())"
                ),
                {"checksum": "backup-notification-test"},
            )
            connection.execute(
                text("DELETE FROM schedule_versions WHERE checksum = :checksum"),
                {"checksum": "backup-notification-test"},
            )

        notification = next(
            listener.notifies(timeout=1, stop_after=1),
            None,
        )

    assert notification is not None
    assert notification.channel == "transit_advisor_backup"
    assert notification.payload == "schedule_versions"
