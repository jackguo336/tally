from datetime import date

from tally.models.db import Config


def create_config(
    challenge_name: str | None = None,
    start_date: str | None = None,
    time_zone: str | None = None,
):
    return Config(
        challenge_name=challenge_name or "Test Challenge",
        start_date=start_date or date.today().isoformat(),
        time_zone=time_zone or "UTC"
    )
