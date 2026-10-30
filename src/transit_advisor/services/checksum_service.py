from hashlib import sha256


class ChecksumService:
    def calculate(
        self,
        content: bytes,
    ) -> str:
        return sha256(content).hexdigest()
