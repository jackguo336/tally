from pydantic import BaseModel
from typing import List, Union


class Athlete(BaseModel):
    athleteId: str
    athleteName: str


class ActivityStatsEntry(BaseModel):
    key: str
    value: str


class FeedActivity(BaseModel):
    id: str
    athlete: Athlete
    activityName: str
    startDate: str
    elapsedTime: int
    stats: List[ActivityStatsEntry]
    type: str


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
