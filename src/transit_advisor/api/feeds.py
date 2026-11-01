from __future__ import annotations

import io
import zipfile
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from transit_advisor.api.dependencies import get_feed_upload_service
from transit_advisor.api.schemas import UploadFeedResponse
from transit_advisor.domain.upload_result import UploadResult
from transit_advisor.services.feed_upload_service import FeedUploadService

router = APIRouter(prefix="/feeds", tags=["feeds"])


@router.post(
    "",
    response_model=UploadFeedResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "Feed with this checksum already exists (duplicate)."},
        422: {"description": "Feed archive failed validation."},
    },
)
async def upload(
    file: UploadFile,
    service: Annotated[FeedUploadService, Depends(get_feed_upload_service)],
) -> UploadFeedResponse:
    archive_bytes = await file.read()

    try:
        archive_files = _list_archive_files(archive_bytes)
    except zipfile.BadZipFile as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Uploaded file is not a valid zip archive.",
        ) from exc

    result: UploadResult = service.upload(archive_bytes, archive_files)

    if not result.imported and not result.duplicate:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Feed archive failed validation.",
        )

    if result.duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Feed with checksum {result.checksum} already exists.",
        )

    return UploadFeedResponse(
        checksum=result.checksum,
        imported=result.imported,
        duplicate=result.duplicate,
    )


def _list_archive_files(archive_bytes: bytes) -> set[str]:
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as zf:
        return set(zf.namelist())
