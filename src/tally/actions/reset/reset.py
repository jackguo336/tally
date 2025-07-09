import questionary

from tally.models.user import User
from tally.models.team import Team
from tally.models.config import Config
from tally.models.activity import Activity
from tally.services.db import backup_db


def reset():
    is_confirm_reset = questionary.confirm(
        "Are you sure you want to delete all user, team and activity data? "
        "A backup will be created in the backups folder."
    ).ask()
    if not is_confirm_reset:
        print("Operation cancelled")
        return
    
    backup_db()

    User.delete().execute()
    Team.delete().execute()
    Activity.delete().execute()
    Config.delete().execute()

    print("All data deleted")
