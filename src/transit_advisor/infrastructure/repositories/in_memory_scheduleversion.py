from transit_advisor.domain.scheduleversion import ScheduleVersion


class InMemoryScheduleVersionRepository:
    def __init__(self) -> None:
        self._versions: dict[str, ScheduleVersion] = {}

    def find_by_checksum(self, checksum: str) -> ScheduleVersion | None:
        return self._versions.get(checksum)

    def save(self, version: ScheduleVersion) -> ScheduleVersion:
        # У ScheduleVersion id: int | None. In-memory репозиторій має
        # згенерувати id, як це зробила б БД.
        if version.id is None:
            version = ScheduleVersion(
                id=len(self._versions) + 1,
                checksum=version.checksum,
                imported_at=version.imported_at,
            )
        self._versions[version.checksum] = version
        return version
