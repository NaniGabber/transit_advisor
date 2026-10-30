from transit_advisor.services.checksum_service import (
    ChecksumService,
)


def test_same_content_produces_same_checksum() -> None:
    service = ChecksumService()

    checksum_1 = service.calculate(
        b"test content",
    )

    checksum_2 = service.calculate(
        b"test content",
    )

    assert checksum_1 == checksum_2


def test_different_content_produces_different_checksums() -> None:
    service = ChecksumService()

    checksum_1 = service.calculate(
        b"first",
    )

    checksum_2 = service.calculate(
        b"second",
    )

    assert checksum_1 != checksum_2


def test_checksum_is_sha256_hash() -> None:
    service = ChecksumService()

    checksum = service.calculate(
        b"test",
    )

    assert len(checksum) == 64
