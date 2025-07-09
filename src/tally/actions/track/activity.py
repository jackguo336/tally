import logging
from datetime import datetime
from typing import List
import re
import time

from tally.services.strava import StravaService
from tally.models.activity import Activity
from tally.models.club_feed import (
    FeedEntryMultipleActivities,
    FeedResponse,
    ActivityStatsEntry,
)


logger = logging.getLogger(__name__)


def get_moving_seconds_from_stats(stats: List[ActivityStatsEntry]) -> int | None:
    moving_seconds = None
    one_minute_in_seconds = 60
    moving_time_regex = r"(\d+)\s*<.*>\s*(\d+)\s*<.*>"
    minutes_group_index = 1
    seconds_group_index = 2

    for entry in stats:
        match = re.search(moving_time_regex, entry.value)
        if match:
            moving_seconds = int(
                match.group(minutes_group_index)
            ) * one_minute_in_seconds + int(match.group(seconds_group_index))
            break

    return moving_seconds


def get_activities_from_feed(feed: FeedResponse) -> List[Activity]:
    activities = []
    for entry in feed.entries:
        entry_activities = (
            entry.rowData.activities
            if isinstance(entry, FeedEntryMultipleActivities)
            else [entry.activity]
        )

        for activity in entry_activities:
            moving_seconds = get_moving_seconds_from_stats(activity.stats)
            if not moving_seconds:
                logger.debug(f"No moving time found for activity {activity.id}")

            activities.append(
                Activity(
                    id=activity.id,
                    user=activity.athlete.athleteId,
                    start_time=datetime.fromisoformat(
                        activity.startDate.replace("Z", "+00:00")
                    ),
                    elapsed_seconds=activity.elapsedTime,
                    moving_seconds=moving_seconds,
                    title=activity.activityName,
                    workout_type=activity.type,
                )
            )
    return activities


def get_activities(
    strava_service: StravaService, team_id: str, after_date: datetime
) -> List[Activity]:
    activities: List[Activity] = []
    cursor = None
    request_interval_seconds = 5
    while True:
        # delay request to avoid rate limiting
        time.sleep(request_interval_seconds)

        feed = strava_service.get_club_feed(team_id, cursor)
        activities.extend(get_activities_from_feed(feed))
        next_feed_timestamp = (
            feed.entries[-1].cursorData.updated_at if feed.entries else None
        )
        # comparing the updated_at timestamp means activities fetch before the
        # after_date but updated after the after_date are still fetched.
        if not feed.pagination.hasMore or next_feed_timestamp < after_date.timestamp():
            break
        cursor = next_feed_timestamp

    return activities
