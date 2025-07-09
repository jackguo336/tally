from peewee import CharField, DateField

from tally.models.base import BaseModel


class Config(BaseModel):
    challenge_name = CharField()
    start_date = DateField()
    end_date = DateField()
    time_zone = CharField()
