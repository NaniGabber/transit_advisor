from pathlib import Path

from tests.services.fake_repos import get_feed_upload_service


def test_upload_valid_feed(tmp_path: Path) -> None:
    container = get_feed_upload_service()
    archive_path = tmp_path / "feed.zip"

    result = container.service.upload(
        archive_path=archive_path,
    )

    assert result.imported
    assert not result.duplicate


def test_reject_duplicate_feed(tmp_path: Path) -> None:
    container = get_feed_upload_service()
    archive_path = tmp_path / "feed.zip"

    container.service.upload(archive_path=archive_path)

    result = container.service.upload(archive_path=archive_path)

    assert result.duplicate
    assert not result.imported


def test_invalid_archive_rejected(tmp_path: Path) -> None:
    container = get_feed_upload_service(
        files={"agency.txt", "routes.txt"},  # Немає обов'язкових файлів
    )
    archive_path = tmp_path / "feed.zip"

    result = container.service.upload(
        archive_path=archive_path,
    )

    assert not result.imported


def test_create_schedule_version_after_upload(tmp_path: Path) -> None:
    container = get_feed_upload_service()
    archive_path = tmp_path / "feed.zip"

    container.service.upload(
        archive_path=archive_path,
    )

    assert len(container.schedule_version_repository.saved) == 1
