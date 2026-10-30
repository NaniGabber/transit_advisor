from pydantic import BaseModel, Field


class UploadFeedResponse(BaseModel):
    checksum: str = Field(..., description="SHA-256 checksum of the uploaded archive.")
    imported: bool = Field(
        ..., description="True if a new schedule version was created."
    )
    duplicate: bool = Field(
        ..., description="True if a version with this checksum already existed."
    )
