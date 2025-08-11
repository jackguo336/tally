from peewee import CharField, ForeignKeyField

from .base import BaseModel
from .team import Team


class User(BaseModel):
    id = CharField(primary_key=True)
    name = CharField()
    team = ForeignKeyField(Team, backref="users")

    def __str__(self):
        return f"User(" f"id={self.id}, " f"name={self.name}, " f"team={self.team})"

    def __repr__(self):
        return self.__str__()
