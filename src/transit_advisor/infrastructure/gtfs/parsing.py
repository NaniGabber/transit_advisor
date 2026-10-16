def normalize(value: str) -> str:
    return " ".join(value.split())


def parse_route_type(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None
