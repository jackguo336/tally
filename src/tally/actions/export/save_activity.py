from typing import List
import csv
import datetime

from tally.models.db import Activity, Config
from tally.utils.activity import get_activity_link, get_activity_active_seconds
from tally.utils.file import prompt_save_file
from tally.utils.date import format_duration, get_file_timestamp, get_local_date
from tally.utils.user import get_user_link


def save_activities(activities: List[Activity], config: Config):
    file = prompt_save_file(f"activities_{get_file_timestamp()}", ".csv", "activities")
    if not file:
        print("No file selected, skipping save")
        return

    with open(file, "w") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "link",
                "user_link",
                "user",
                "title",
                "workout_type",
                "date",
                "active_time",
            ]
        )
        for activity in activities:
            writer.writerow(
                [
                    get_activity_link(activity),
                    get_user_link(activity.user),
                    activity.user.name,
                    activity.title,
                    activity.workout_type,
                    get_local_date(
                        datetime.datetime.fromisoformat(activity.start_time),
                        config.time_zone,
                    ).strftime("%Y-%m-%d"),
                    format_duration(get_activity_active_seconds(activity)),
                ]
            )

    print(f"Successfully saved {len(activities)} activities to {file}")
