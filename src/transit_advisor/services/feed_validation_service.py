class FeedValidator:
    REQUIRED_FILES = {
        "agency.txt",
        "routes.txt",
        "stops.txt",
        "trips.txt",
        "stop_times.txt",
    }

    def validate(
        self,
        file_names: set[str],
    ) -> bool:
        return self.REQUIRED_FILES.issubset(
            file_names,
        )
