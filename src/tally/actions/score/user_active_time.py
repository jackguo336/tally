import datetime
from typing import List, Tuple
import pytz

from tally.models.db import Activity, User
from tally.actions.score.score_config import ScoreConfig
from tally.utils.activity import get_activity_active_seconds


class UserActiveTime:
    def __init__(self, user: User, date: datetime.date, active_seconds: int = 0):
        self.user = user
        self.date = date
        self.active_seconds = active_seconds

    def add_activity(self, activity: Activity):
        self.active_seconds += get_activity_active_seconds(activity)

    def __str__(self):
        return (
            f"UserActiveTime("
            f"user={self.user.id}, "
            f"date={self.date}, "
            f"active_seconds={self.active_seconds})"
        )

    def __repr__(self):
        return self.__str__()


def get_user_active_time(
    activities: List[Activity], config: ScoreConfig
) -> List[UserActiveTime]:
    active_time_map = dict[Tuple[str, datetime.date], UserActiveTime]()

    for activity in activities:
        activity_date = (
            datetime.datetime.fromisoformat(activity.start_time)
            .astimezone(pytz.timezone(config.time_zone))
            .date()
        )
        if (
            activity_date > config.score_end_date
            or activity_date < config.score_start_date
        ):
            continue

        key = (activity.user.id, activity_date)
        active_time = active_time_map.get(
            key, UserActiveTime(activity.user, activity_date)
        )
        active_time.add_activity(activity)
        active_time_map[key] = active_time

    return list(active_time_map.values())
