from typing import List
import questionary
import datetime

from tally.models.config import Config
from tally.models.team import Team
from tally.models.user import User
from tally.models.activity import Activity
from tally.actions.score.score_config import ScoreConfig
from tally.actions.score.save_score import save_team_cumulative_score_to_csv
from tally.utils.date import (
    date_validator,
)
from tally.actions.score.user_active_time import (
    get_user_active_time,
)
from tally.actions.score.user_score import get_user_daily_score
from tally.actions.score.team_score import get_team_daily_score, get_team_cumulative_score


def prompt_date(message: str, default: datetime.date) -> datetime.date:
    date = questionary.text(
        message,
        validate=date_validator,
        default=default.strftime("%Y-%m-%d"),
    ).ask()
    return datetime.datetime.strptime(date, "%Y-%m-%d").date()


def prompt_score_start_date(default_start_date: datetime.date) -> datetime.date:
    return prompt_date(
        "Enter the start date for the score calculation (YYYY-MM-DD)",
        default_start_date,
    )


def prompt_score_end_date():
    return prompt_date(
        "Enter the end date for the score calculation (YYYY-MM-DD)",
        # Default to yesterday's date
        datetime.datetime.now() - datetime.timedelta(days=1),
    )


def score():
    config: Config | None = Config.select().first()
    if not config:
        print(
            "No active challenge found. Start a new challenge first. Cancelling operation."
        )
        return

    score_start_date = prompt_score_start_date(config.start_date)
    score_end_date = prompt_score_end_date()

    score_config = ScoreConfig(score_start_date, score_end_date, config.time_zone)

    activities: List[Activity] = (
        Activity.select().join(User).join(Team).order_by(Activity.start_time.asc())
    )
    users: List[User] = User.select().join(Team)

    user_active_times = get_user_active_time(activities, score_config)
    user_daily_scores = get_user_daily_score(user_active_times)
    team_daily_scores = get_team_daily_score(user_daily_scores, users)
    team_cumulative_scores = get_team_cumulative_score(team_daily_scores, users)

    formatted_team_scores = "\n".join(
        [f"{score.team.name}: {score.points}" for score in team_cumulative_scores]
    )
    print(f"Team scores:\n{formatted_team_scores}")

    save_team_cumulative_score_to_csv(team_cumulative_scores, score_config)
