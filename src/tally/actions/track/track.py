import logging
from typing import List
import datetime

from tally.models.db import Config, Team, Activity
from tally.actions.track.activity import get_activities
from tally.services.strava import StravaService
from tally.utils.date import get_start_of_day
from tally.services.db import backup_db


logger = logging.getLogger(__name__)


def track():
    config: Config | None = Config.select().first()
    if not config:
        print(
            "No active challenge found. Start a new challenge first. Cancelling operation."
        )
        return

    challenge_start_time = get_start_of_day(config.start_date, config.time_zone)
    # Avoid fetching already saved activities
    last_activity: Activity | None = (
        Activity.select().order_by(Activity.start_time.desc()).first()
    )
    last_tracked_time = (
        datetime.datetime.fromisoformat(last_activity.start_time)
        if last_activity
        else challenge_start_time
    )

    teams: List[Team] = Team.select()
    activities: List[Activity] = []
    print("Please wait, a browser window is opening...")
    strava_service = StravaService()
    strava_service.login()
    for team in teams:
        print(f"Fetching activities for team {team.id}")
        activities.extend(get_activities(strava_service, team, last_tracked_time))
        print(f"Fetched {len(activities)} activities for team {team.id}")

    saved_activity_count = 0
    for activity in activities:
        # Drop activities that occurred before the challenge started
        if activity.start_time < challenge_start_time:
            continue

        # Do not overwrite existing activities in DB to prevent edits made by
        # the user and imported using the load action from being lost
        Activity.insert(**activity.__data__).on_conflict_ignore().execute()

        logger.debug(f"Saved {activity}")
        saved_activity_count += 1

    print(f"Saved {saved_activity_count} activities after {last_tracked_time}")

    backup_db()
