import logging
from datetime import datetime
from typing import List
import re
import time

from tally.services.strava import StravaService
from tally.models.db import Activity, Team
from tally.models.validation.club_feed import (
    FeedEntryMultipleActivities,
    FeedResponse,
    FeedActivity,
    ActivityStatsEntry,
)


logger = logging.getLogger(__name__)


def get_moving_seconds_from_stats(stats: List[ActivityStatsEntry]) -> int | None:
    """
    Checks if the stats string contains any one or more of the following elements:
    - Seconds: "{{seconds}}<abbr class='unit' title='second'>s</abbr>"
    - Minutes: "{{minutes}}<abbr class='unit' title='minute'>m</abbr>"
    - Hours: "{{hours}}<abbr class='unit' title='hour'>h</abbr>"
    If so, extract the values and convert to seconds.
    """

    one_minute_in_seconds = 60
    one_hour_in_seconds = 3600

    # Separate regexes for each time unit
    hour_regex = r"(\d+)\s*<[^>]*title='hour'[^>]*>"
    minute_regex = r"(\d+)\s*<[^>]*title='minute'[^>]*>"
    second_regex = r"(\d+)\s*<[^>]*title='second'[^>]*>"

    for entry in stats:
        # Search for each time unit independently
        hour_match = re.search(hour_regex, entry.value)
        minute_match = re.search(minute_regex, entry.value)
        second_match = re.search(second_regex, entry.value)

        # The stats string isn't a moving time if it doesn't contain hours,
        # minutes, or seconds
        if not (hour_match or minute_match or second_match):
            continue

        hours = int(hour_match.group(1)) if hour_match else 0
        minutes = int(minute_match.group(1)) if minute_match else 0
        seconds = int(second_match.group(1)) if second_match else 0
        
        moving_seconds = (
            hours * one_hour_in_seconds + 
            minutes * one_minute_in_seconds + 
            seconds
        )
        return moving_seconds

    return None


def get_activities_from_feed(feed: FeedResponse) -> List[FeedActivity]:
    feed_activities = []
    for entry in feed.entries:
        entry_activities = (
            entry.rowData.activities
            if isinstance(entry, FeedEntryMultipleActivities)
            else [entry.activity]
        )

        for activity in entry_activities:
            feed_activities.append(activity)

    return feed_activities


def map_feed_activity_to_activity(activity: FeedActivity) -> Activity:
    moving_seconds = get_moving_seconds_from_stats(activity.stats)
    if not moving_seconds:
        logger.debug(f"No moving time found for activity {activity.id}")

    return Activity(
        id=activity.id,
        user=activity.athlete.athleteId,
        start_time=datetime.fromisoformat(activity.startDate.replace("Z", "+00:00")),
        elapsed_seconds=activity.elapsedTime,
        moving_seconds=moving_seconds,
        title=activity.activityName,
        workout_type=activity.type,
    )


def get_activities(
    strava_service: StravaService, team: Team, after_date: datetime
) -> List[Activity]:
    feed_activities: List[FeedActivity] = []
    cursor = None
    request_interval_seconds = 5
    while True:
        # delay request to avoid rate limiting
        time.sleep(request_interval_seconds)

        feed = strava_service.get_club_feed(team.id, cursor)
        feed_activities.extend(get_activities_from_feed(feed))
        next_feed_timestamp = (
            feed.entries[-1].cursorData.updated_at if feed.entries else None
        )
        # comparing the updated_at timestamp means activities fetch before the
        # after_date but updated after the after_date are still fetched.
        if not feed.pagination.hasMore or next_feed_timestamp < after_date.timestamp():
            break
        cursor = next_feed_timestamp

    # If the user is part of a team in Strava, but not a part of the team in the
    # database, use the database as the source of truth and do not include the activity.
    team_user_id_set = {user.id for user in team.users}
    activities = []
    for activity in feed_activities:
        if activity.athlete.athleteId in team_user_id_set:
            activities.append(map_feed_activity_to_activity(activity))
        else:
            logger.debug(
                f"Excluding activity {activity.id}. "
                f"User {activity.athlete.athleteId} is not in team {team.id}"
            )

    return activities
