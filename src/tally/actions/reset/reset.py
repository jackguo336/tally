import questionary

from tally.services.db import db, backup_db
from tally.models.db import ALL_MODELS


def reset():
    is_confirm_reset = questionary.confirm(
        "Are you sure you want to delete all user, team and activity data? "
        "A backup will be created in the backups folder."
    ).ask()
    if not is_confirm_reset:
        print("Operation cancelled")
        return

    backup_db()

    db.drop_tables(ALL_MODELS)

    print("All data deleted")
