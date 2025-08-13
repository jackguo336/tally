from uuid import uuid4

from tally.models.db import User


def create_user(
    id: str | None,
    name: str | None,
    team: str | None,
):
    return User(
        id=id or str(uuid4()), name=name or "John Smith", team=team or str(uuid4())
    )
