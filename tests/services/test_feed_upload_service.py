from .fake_repos import get_feed_upload_service


def test_upload_valid_feed() -> None:
    container = get_feed_upload_service()

    result = container.service.upload(
        archive_bytes=b"valid archive",
        archive_files={
            "agency.txt",
            "routes.txt",
            "stops.txt",
            "trips.txt",
            "stop_times.txt",
        },
    )

    assert result.imported
    assert not result.duplicate


def test_reject_duplicate_feed() -> None:
    container = get_feed_upload_service()

    archive = b"same archive"

    container.service.upload(
        archive_bytes=archive,
        archive_files={
            "agency.txt",
            "routes.txt",
            "stops.txt",
            "trips.txt",
            "stop_times.txt",
        },
    )

    result = container.service.upload(
        archive_bytes=archive,
        archive_files={
            "agency.txt",
            "routes.txt",
            "stops.txt",
            "trips.txt",
            "stop_times.txt",
        },
    )

    assert result.duplicate
    assert not result.imported


def test_invalid_archive_rejected() -> None:
    container = get_feed_upload_service()

    result = container.service.upload(
        archive_bytes=b"archive",
        archive_files={
            "agency.txt",
            "routes.txt",
        },
    )

    assert not result.imported


def test_create_schedule_version_after_upload() -> None:
    container = get_feed_upload_service()

    container.service.upload(
        archive_bytes=b"valid archive",
        archive_files={
            "agency.txt",
            "routes.txt",
            "stops.txt",
            "trips.txt",
            "stop_times.txt",
        },
    )

    assert len(container.schedule_version_repository.saved) == 1
