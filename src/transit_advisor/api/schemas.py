from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UploadFeedResponse(BaseModel):
    checksum: str = Field(..., description="SHA-256 checksum of the uploaded archive.")
    imported: bool = Field(
        ..., description="True if a new schedule version was created."
    )
    duplicate: bool = Field(
        ..., description="True if a version with this checksum already existed."
    )


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique notification identifier.")
    user_id: int = Field(
        ..., description="ID of the user who receives the notification."
    )
    subscription_id: int = Field(
        ..., description="ID of the subscription that triggered the notification."
    )
    schedule_version_id: int = Field(
        ..., description="ID of the schedule version the notification refers to."
    )
    message: str = Field(..., description="Human-readable notification text.")
    created_at: datetime = Field(
        ..., description="Timestamp when the notification was created (UTC)."
    )
    is_read: bool = Field(
        ..., description="True if the user has already read the notification."
    )
