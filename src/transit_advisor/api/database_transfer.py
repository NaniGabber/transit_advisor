from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from transit_advisor.api.auth import Role, require_role
from transit_advisor.api.dependencies import (
    get_database_transfer_service,
    get_session,
)
from transit_advisor.domain.exceptions import InvalidDatabaseSnapshotError
from transit_advisor.services.database_transfer_service import DatabaseTransferService

router = APIRouter(prefix="/api/v1/admin/database", tags=["database"])
MAX_SNAPSHOT_SIZE = 100 * 1024 * 1024


@router.get(
    "/export",
    dependencies=[Depends(require_role(Role.ADMIN))],
    responses={403: {"description": "Only admin can export the database."}},
)
def export_database(
    service: Annotated[
        DatabaseTransferService,
        Depends(get_database_transfer_service),
    ],
) -> Response:
    snapshot = service.export_snapshot()
    filename = f"transit-database-{datetime.now(UTC):%Y%m%dT%H%M%SZ}.json"
    return Response(
        content=snapshot,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/import",
    dependencies=[Depends(require_role(Role.ADMIN))],
    responses={
        403: {"description": "Only admin can import a database snapshot."},
        413: {"description": "Database snapshot exceeds the size limit."},
        422: {"description": "Invalid database snapshot."},
    },
)
def import_database(
    file: Annotated[UploadFile, File()],
    confirm: Annotated[bool, Form()],
    service: Annotated[
        DatabaseTransferService,
        Depends(get_database_transfer_service),
    ],
    session: Annotated[Session, Depends(get_session)],
) -> dict[str, dict[str, int]]:
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Set confirm=true to replace the application database data.",
        )

    snapshot = file.file.read(MAX_SNAPSHOT_SIZE + 1)
    if len(snapshot) > MAX_SNAPSHOT_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Database snapshot exceeds the 100 MiB limit.",
        )

    try:
        with session.begin():
            imported = service.import_snapshot(snapshot)
    except InvalidDatabaseSnapshotError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    return {"imported": imported}
