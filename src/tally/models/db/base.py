from peewee import Model

from tally.services.db import db


class BaseModel(Model):
    class Meta:
        database = db
