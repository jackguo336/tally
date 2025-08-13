from uuid import uuid4
from datetime import datetime, timezone

from tally.models.db import Activity, User


def create_activity(
    id: str | None = None,
    user: str | None = None,
    start_time: str | None = None,
    elapsed_seconds: int | None = None,
    moving_seconds: int | None = None,
    title: str | None = None,
    workout_type: str | None = None,
):
    return Activity(
        id=id or str(uuid4()),
        user=user or str(uuid4()),
        start_time=start_time or datetime.now(timezone.utc),
        elapsed_seconds=elapsed_seconds or 3600,
        moving_seconds=moving_seconds,
        title=title or "Test Activity",
        workout_type=workout_type or "Run",
    )
