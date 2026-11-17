import logging
from hashlib import sha256
from pathlib import Path

logger = logging.getLogger(__name__)


class ChecksumService:
    def calculate(
        self,
        content: bytes,
    ) -> str:
        checksum = sha256(content).hexdigest()
        logger.debug("checksum_calculated bytes=%s", len(content))
        return checksum

    def calculate_from_file(self, path: Path) -> str:
        hasher = sha256()
        bytes_read = 0
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
            bytes_read += len(chunk)
        checksum = hasher.hexdigest()
        logger.debug("file_checksum_calculated bytes=%s", bytes_read)
        return checksum
