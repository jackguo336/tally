from uuid import uuid4
from datetime import datetime, timezone
from typing import List, Union
import time

from tally.models.validation.club_feed import (
    Athlete,
    ActivityStatsEntry,
    FeedActivity,
    RowData,
    CursorData,
    FeedEntrySingleActivity,
    FeedEntryMultipleActivities,
    FeedResponsePagination,
    FeedResponse,
)


def create_athlete(
    athlete_id: str | None = None,
    athlete_name: str | None = None,
) -> Athlete:
    return Athlete(
        athleteId=athlete_id or str(uuid4()), athleteName=athlete_name or "Test Athlete"
    )


def create_activity_stats_entry(
    key: str | None = None,
    value: str | None = None,
) -> ActivityStatsEntry:
    return ActivityStatsEntry(key=key or "distance", value=value or "5.2 km")


def create_feed_activity(
    id: str | None = None,
    athlete: Athlete | None = None,
    activity_name: str | None = None,
    start_date: str | None = None,
    elapsed_time: int | None = None,
    stats: List[ActivityStatsEntry] | None = None,
    activity_type: str | None = None,
) -> FeedActivity:
    return FeedActivity(
        id=id or str(uuid4()),
        athlete=athlete or create_athlete(),
        activityName=activity_name or "Test Activity",
        startDate=start_date or datetime.now(timezone.utc).isoformat(),
        elapsedTime=elapsed_time or 3600,
        stats=stats or [create_activity_stats_entry()],
        type=activity_type or "Run",
    )


def create_row_data(
    activities: List[FeedActivity] | None = None,
) -> RowData:
    return RowData(activities=activities or [create_feed_activity()])


def create_cursor_data(
    updated_at: int | None = None,
) -> CursorData:
    return CursorData(updated_at=updated_at or int(time.time()))


def create_feed_entry_single_activity(
    cursor_data: CursorData | None = None,
    activity: FeedActivity | None = None,
) -> FeedEntrySingleActivity:
    return FeedEntrySingleActivity(
        cursorData=cursor_data or create_cursor_data(),
        activity=activity or create_feed_activity(),
    )


def create_feed_entry_multiple_activities(
    cursor_data: CursorData | None = None,
    row_data: RowData | None = None,
) -> FeedEntryMultipleActivities:
    return FeedEntryMultipleActivities(
        cursorData=cursor_data or create_cursor_data(),
        rowData=row_data or create_row_data(),
    )


def create_feed_response_pagination(
    has_more: bool | None = None,
) -> FeedResponsePagination:
    return FeedResponsePagination(hasMore=has_more if has_more is not None else False)


def create_feed_response(
    entries: (
        List[Union[FeedEntrySingleActivity, FeedEntryMultipleActivities]] | None
    ) = None,
    pagination: FeedResponsePagination | None = None,
) -> FeedResponse:
    return FeedResponse(
        entries=entries or [create_feed_entry_single_activity()],
        pagination=pagination or create_feed_response_pagination(),
    )
