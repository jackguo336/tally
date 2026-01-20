from pydantic import BaseModel, model_validator
from typing import List, Union, Optional


class Athlete(BaseModel):
    athleteId: str
    athleteName: str


class ActivityStatsEntry(BaseModel):
    key: str
    value: str


class FeedActivity(BaseModel):
    # Standard activity fields
    id: str
    athlete: Athlete
    activityName: str
    startDate: str
    elapsedTime: int

    # Alternate activity fields in variant B (optional, only present in variant B format)
    activity_id: Optional[int] = None
    entity_id: Optional[int] = None
    athlete_id: Optional[int] = None
    athlete_name: Optional[str] = None
    name: Optional[str] = None
    start_date: Optional[str] = None
    elapsed_time: Optional[int] = None

    # Common fields between standard and variants
    stats: List[ActivityStatsEntry]
    type: str

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data):
        """Normalize field names from API response to model fields"""
        if not isinstance(data, dict):
            return data

        # Handle entity_id or activity_id -> id
        if data.get("id") is None:
            if data.get("entity_id") is not None:
                data["id"] = str(data["entity_id"])
            elif data.get("activity_id") is not None:
                data["id"] = str(data["activity_id"])

        # Handle athlete_id and athlete_name -> athlete object
        if (
            data.get("athlete") is None
            and data.get("athlete_id") is not None
            and data.get("athlete_name") is not None
        ):
            data["athlete"] = {
                "athleteId": str(data.get("athlete_id")),
                "athleteName": data.get("athlete_name"),
            }

        # Handle name -> activityName
        if data.get("activityName") is None and data.get("name") is not None:
            data["activityName"] = data["name"]

        # Handle start_date -> startDate
        if data.get("startDate") is None and data.get("start_date") is not None:
            data["startDate"] = data["start_date"]

        # Handle elapsed_time -> elapsedTime
        if data.get("elapsedTime") is None and data.get("elapsed_time") is not None:
            data["elapsedTime"] = data["elapsed_time"]

        return data


class RowData(BaseModel):
    activities: List[FeedActivity]


class CursorData(BaseModel):
    updated_at: int


class BaseFeedEntry(BaseModel):
    cursorData: CursorData


class FeedEntrySingleActivity(BaseFeedEntry):
    activity: FeedActivity


class FeedEntryMultipleActivities(BaseFeedEntry):
    rowData: RowData


class FeedResponsePagination(BaseModel):
    hasMore: bool


class FeedResponse(BaseModel):
    entries: List[Union[FeedEntrySingleActivity, FeedEntryMultipleActivities]]
    pagination: FeedResponsePagination
