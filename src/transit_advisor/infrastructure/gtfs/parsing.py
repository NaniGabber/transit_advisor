def normalize(value: str) -> str:
    return " ".join(value.split())


def parse_int(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def parse_float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None
