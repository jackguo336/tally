from typing import List, Tuple
import datetime

from tally.models.db import User
from tally.actions.score.user_active_time import UserActiveTime
from tally.utils.date import get_previous_day
from tally.actions.score.point_system import (
    calculate_user_points,
    calculate_user_bonus_points,
)


class UserDailyScore:
    def __init__(self, user: User, date: datetime.date, points: int):
        self.user = user
        self.date = date
        self.points = points

    def __str__(self):
        return (
            f"UserDailyScore("
            f"user={self.user.id}, "
            f"date={self.date}, "
            f"points={self.points})"
        )

    def __repr__(self):
        return self.__str__()


def get_user_daily_score(
    user_active_times: List[UserActiveTime],
) -> List[UserDailyScore]:
    user_daily_scores: List[UserDailyScore] = []
    user_streak_map = dict[Tuple[str, datetime.date], int]()

    for active_time_entry in user_active_times:
        points = calculate_user_points(active_time_entry.active_seconds)
        prev_day_date = get_previous_day(active_time_entry.date)
        prev_streak = user_streak_map.get((active_time_entry.user.id, prev_day_date), 0)
        streak = prev_streak + 1 if active_time_entry.active_seconds > 0 else 0
        bonus_points = calculate_user_bonus_points(streak)

        user_daily_scores.append(
            UserDailyScore(
                active_time_entry.user,
                active_time_entry.date,
                points + bonus_points,
            )
        )

    return user_daily_scores
