from peewee import CharField

from .base import BaseModel


class Team(BaseModel):
    id = CharField(primary_key=True)
    name = CharField()

    def __str__(self):
        return f"Team(" f"id={self.id}, " f"name={self.name})"

    def __repr__(self):
        return self.__str__()
