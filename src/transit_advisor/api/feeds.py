from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
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
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        result: UploadResult = service.upload(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)
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
