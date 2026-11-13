import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from transit_advisor.api.auth import Role, require_role
from transit_advisor.api.dependencies import get_feed_upload_service, get_session
from transit_advisor.api.schemas import ImportStatsResponse, UploadFeedResponse
from transit_advisor.domain.upload_result import UploadResult
from transit_advisor.services.feed_upload_service import FeedUploadService

router = APIRouter(
    prefix="/feeds",
    tags=["feeds"],
)


@router.post(
    "",
    response_model=UploadFeedResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.ADMIN))],
    responses={
        403: {"description": "Only admin can upload feeds."},
        409: {"description": "Feed with this checksum already exists."},
        422: {"description": "Invalid GTFS archive or not a zip file."},
    },
)
def upload_feed(
    file: UploadFile,
    service: Annotated[
        FeedUploadService,
        Depends(get_feed_upload_service),
    ],
    session: Annotated[
        Session,
        Depends(get_session),
    ],
) -> UploadFeedResponse:
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="File must be a .zip archive.",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        try:
            with zipfile.ZipFile(tmp_path):
                pass
        except zipfile.BadZipFile as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="File is not a valid zip archive.",
            ) from exc

        with session.begin():
            result: UploadResult = service.upload(tmp_path)

        if not result.imported and not result.duplicate:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Feed validation failed. Missing required GTFS files.",
            )

        if result.duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Feed with this checksum already exists.",
            )

        return UploadFeedResponse(
            checksum=result.checksum,
            imported=result.imported,
            duplicate=result.duplicate,
            stats={
                key: ImportStatsResponse(imported=stat.imported, rejected=stat.rejected)
                for key, stat in result.stats.items()
            },
        )
    finally:
        tmp_path.unlink(missing_ok=True)
