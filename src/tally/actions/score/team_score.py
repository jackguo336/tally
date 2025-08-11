from typing import List, Tuple, Optional
import datetime

from tally.models.db import Team, User
from tally.actions.score.user_score import UserDailyScore
from tally.actions.score.point_system import calculate_team_bonus_points


class TeamDailyScore:
    def __init__(
        self,
        team: Team,
        date: datetime.date,
        users: List[User],
        user_scores: Optional[List[UserDailyScore]] = None,
    ):
        self.team = team
        self.date = date
        self.users = users
        self.user_scores = user_scores or []

    def add_user_score(self, user_score: UserDailyScore):
        self.user_scores.append(user_score)

    def get_points(self) -> int:
        points = sum(user_score.points for user_score in self.user_scores)

        active_user_count = len(
            [user_score for user_score in self.user_scores if user_score.points > 0]
        )
        total_user_count = len(self.users)
        bonus_points = calculate_team_bonus_points(active_user_count, total_user_count)

        return points + bonus_points

    def __str__(self):
        return (
            f"TeamDailyScore("
            f"team={self.team.id}, "
            f"date={self.date}, "
            f"user_scores={self.user_scores})"
        )

    def __repr__(self):
        return self.__str__()


class TeamCumulativeScore:
    def __init__(self, team: Team, points: int = 0):
        self.team = team
        self.points = points

    def add_daily_score(self, daily_score: TeamDailyScore):
        self.points += daily_score.get_points()

    def __str__(self):
        return f"TeamCumulativeScore(" f"team={self.team.id}, " f"points={self.points})"

    def __repr__(self):
        return self.__str__()


def get_team_daily_score(
    user_daily_scores: List[UserDailyScore], users: List[User]
) -> List[TeamDailyScore]:
    team_user_map = dict[str, List[User]]()
    for user in users:
        team_user_map[user.team.id] = team_user_map.get(user.team.id, []) + [user]

    team_score_map = dict[Tuple[str, datetime.date], TeamDailyScore]()

    for user_score_entry in user_daily_scores:
        team: Team = user_score_entry.user.team
        date = user_score_entry.date
        key = (team.id, date)

        team_score = team_score_map.get(
            key, TeamDailyScore(team, date, team_user_map[team.id])
        )
        team_score.add_user_score(user_score_entry)
        team_score_map[key] = team_score

    return list(team_score_map.values())


def get_team_cumulative_score(
    team_daily_scores: List[TeamDailyScore], users: List[User]
) -> List[TeamCumulativeScore]:
    team_score_map = dict[str, TeamCumulativeScore]()
    for user in users:
        # This ensure that teams with no user score entries are still included
        team_score_map[user.team.id] = TeamCumulativeScore(user.team)

    for team_daily_score in team_daily_scores:
        team: Team = team_daily_score.team

        team_score = team_score_map.get(team.id, TeamCumulativeScore(team))
        team_score.add_daily_score(team_daily_score)
        team_score_map[team.id] = team_score

    team_scores = list(team_score_map.values())
    team_scores.sort(key=lambda x: x.points, reverse=True)
    return team_scores
