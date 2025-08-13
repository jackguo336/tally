from uuid import uuid4

from tally.models.db import Team


def create_team(id: str | None, name: str | None):
    return Team(id=id or str(uuid4()), name=name or "Test Team")
