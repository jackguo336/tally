from uuid import uuid4

from tally.models.db import User


def create_user(
    id: str | None,
    name: str | None,
):
    return User(
        id = id or uuid4(),
        name = name or "John Smith"
    )


