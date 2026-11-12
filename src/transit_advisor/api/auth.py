from collections.abc import Callable
from enum import StrEnum

from fastapi import Header, HTTPException, status


class Role(StrEnum):
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


def require_role(*allowed_roles: Role) -> Callable[[str], None]:
    def checker(x_role: str = Header(default="guest")) -> None:
        try:
            role = Role(x_role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {x_role}",
            ) from None

        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' is not allowed. Required: {allowed_roles}",
            )

    return checker
