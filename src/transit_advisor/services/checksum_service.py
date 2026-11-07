from hashlib import sha256
from pathlib import Path


class ChecksumService:
    def calculate(
        self,
        content: bytes,
    ) -> str:
        return sha256(content).hexdigest()

    def calculate_from_file(self, path: Path) -> str:
        hasher = sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
