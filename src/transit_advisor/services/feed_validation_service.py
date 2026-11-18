import logging

logger = logging.getLogger(__name__)


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
        missing_files = self.REQUIRED_FILES - file_names
        is_valid = not missing_files
        logger.debug(
            "feed_validation_completed valid=%s missing_files=%s",
            is_valid,
            sorted(missing_files),
        )
        return is_valid
