from peewee import CharField, DateField

from .base import BaseModel


class Config(BaseModel):
    challenge_name = CharField()
    start_date = DateField()
    time_zone = CharField()
