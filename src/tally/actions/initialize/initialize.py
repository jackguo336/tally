from typing import List
import logging
import questionary
from pytz import common_timezones

from tally.utils.date import prompt_date
from tally.actions.initialize.user_list import (
    parse_user_list,
    UserRow,
)
from tally.actions.initialize.create_tables import create_tables
from tally.models.db import Config, User, Team
from tally.services.db import backup_db
from tally.utils.file import prompt_select_file, FileType


logger = logging.getLogger(__name__)


def create_teams(user_list: List[UserRow]) -> List[str]:
    team_ids = set()
    for user_row in user_list:
        if user_row.team_id in team_ids:
            logger.debug(f"Skipping duplicate team creation for ID: {user_row.team_id}")
            continue

        team = Team(
            id=user_row.team_id,
            name=user_row.team_name,
        )
        Team.replace(**team.__data__).execute()

        print(f"Created {team}")
        team_ids.add(user_row.team_id)
    return list(team_ids)


def create_users(user_list: List[UserRow]) -> List[str]:
    user_ids = set()
    for user_row in user_list:
        user_id = user_row.get_user_id()
        if user_id in user_ids:
            logger.debug(f"Skipping duplicate user creation for ID: {user_id}")
            continue

        user = User(
            id=user_id,
            name=user_row.user_name,
            team=user_row.team_id,
        )
        User.replace(**user.__data__).execute()

        print(f"Created {user}")
        user_ids.add(user_id)
    return list(user_ids)


def prompt_config(existing_config: Config | None) -> Config | None:
    challenge_name = questionary.text(
        "Enter a name for the challenge",
        default=existing_config.challenge_name if existing_config else "",
    ).ask()
    if not challenge_name:
        return None

    start_date = prompt_date(
        "Enter the start date of the challenge (in format YYYY-MM-DD, e.g. 2025-01-01)",
        existing_config.start_date if existing_config else None,
    )
    if not start_date:
        return None

    time_zone = questionary.select(
        "Select a time zone. Daily scores will be calculated based on this time zone.",
        choices=common_timezones,
        default=existing_config.time_zone if existing_config else "America/Los_Angeles",
    ).ask()
    if not time_zone:
        return None

    return Config(
        challenge_name=challenge_name,
        start_date=start_date,
        time_zone=time_zone,
    )


def initialize():
    create_tables()

    existing_config: Config | None = Config.select().first()
    config = prompt_config(existing_config)
    if not config:
        print("Config is incomplete, cancelling operation")
        return

    # Delete existing config entries so the config that is fetched is always the
    # latest one
    Config.delete().execute()
    config.save()
    logger.debug(f"Created {config}")

    print("Use the pop-up file explorer to select the user list for the challenge")
    user_list_path = prompt_select_file("user table", [FileType.csv])
    if not user_list_path:
        print("No file selected, cancelling operation")
        return

    try:
        user_list = parse_user_list(user_list_path)
    except Exception as e:
        print(f"Failed to read user table\n{e}")
        return

    team_ids = create_teams(user_list)
    user_ids = create_users(user_list)

    print(f"Created {len(team_ids)} team(s) and {len(user_ids)} user(s)")

    backup_db()
