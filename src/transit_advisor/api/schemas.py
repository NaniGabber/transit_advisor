from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ImportStatsResponse(BaseModel):
    imported: int
    rejected: int


class UploadFeedResponse(BaseModel):
    checksum: str = Field(..., description="SHA-256 checksum of the uploaded archive.")
    imported: bool = Field(
        ..., description="True if a new schedule version was created."
    )
    duplicate: bool = Field(
        ..., description="True if a version with this checksum already existed."
    )
    stats: dict[str, ImportStatsResponse]


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


class CreateSubscriptionRequest(BaseModel):
    user_id: int = Field(
        ...,
        description="Identifier of the subscribed user.",
    )

    route_id: int = Field(
        ...,
        description="Internal route identifier.",
    )


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    route_id: int
    is_active: bool


class RouteDiffResponse(BaseModel):
    from_version: int
    to_version: int
    added_routes: list[str]
    removed_routes: list[str]
    changed_stop_times: dict[str, list[int]]


class RouteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agency_id: int
    route_id: str
    short_name: str
    long_name: str
    route_type: int


class DepartureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trip_id: int = Field(..., description="Internal trip ID.")
    stop_id: int = Field(..., description="Internal stop ID.")
    arrival_time: str = Field(..., description="Arrival time (HH:MM:SS).")
    departure_time: str = Field(..., description="Departure time (HH:MM:SS).")
    stop_sequence: int = Field(..., description="Sequence of the stop in the trip.")


class JourneyResponse(BaseModel):
    trip_id: int
    from_stop_id: int
    to_stop_id: int
    departure_time: str
    arrival_time: str
    stop_sequence_start: int
    stop_sequence_end: int


class TripsByDayResponse(BaseModel):
    route_id: int
    trips_by_day: dict[str, int]


class AverageHeadwayResponse(BaseModel):
    route_id: int
    average_headway_minutes: float | None


class TopStopResponse(BaseModel):
    stop_id: int
    route_count: int


class TopStopsResponse(BaseModel):
    stops: list[TopStopResponse]
