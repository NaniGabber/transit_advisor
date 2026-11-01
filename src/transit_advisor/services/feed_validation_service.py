class FeedValidator:
    REQUIRED_FILES = {
        "agency.txt",
        "routes.txt",
        "stops.txt",
        "trips.txt",
        "stop_times.txt",
    }

    def __init__(self, required_files: frozenset[str] | None = None) -> None:
        self._required_files = required_files or self.REQUIRED_FILES

    def validate(
        self,
        file_names: set[str],
    ) -> bool:
        return self.REQUIRED_FILES.issubset(
            file_names,
        )
