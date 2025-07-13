from typing import List
import logging
import datetime

from tally.services.db import backup_db
from tally.utils.file import prompt_select_file, FileType
from tally.actions.load.activity_list import parse_activity_list, ActivityRow
from tally.models.activity import Activity
from tally.utils.date import get_start_of_day
from tally.models.config import Config


logger = logging.getLogger(__name__)


def create_activities(activity_list: List[ActivityRow], config: Config) -> List[str]:
    activity_ids = set()
    for activity_row in activity_list:
        active_seconds = activity_row.get_active_seconds()
        activity = Activity(
            id=activity_row.get_activity_id(),
            user=activity_row.get_user_id(),
            start_time=get_start_of_day(
                datetime.datetime.strptime(activity_row.date, "%Y-%m-%d").date(),
                config.time_zone,
            ),
            elapsed_seconds=active_seconds,
            moving_seconds=active_seconds,
            title=activity_row.title,
            workout_type=activity_row.workout_type,
        )
        Activity.replace(**activity.__data__).execute()

        print(f"Created {activity}")
        activity_ids.add(activity_row.get_activity_id())

    return list(activity_ids)


def load():
    config: Config | None = Config.select().first()
    if not config:
        print(
            "No active challenge found. Start a new challenge first. Cancelling operation."
        )
        return

    print("Use the pop-up file explorer to select the activity list to load")
    activity_list_path = prompt_select_file("activity list", [FileType.csv])
    if not activity_list_path:
        print("No file selected, cancelling operation")
        return

    activity_list = parse_activity_list(activity_list_path)
    activity_ids = create_activities(activity_list, config)
    print(f"Created {len(activity_ids)} activities")

    backup_db()
