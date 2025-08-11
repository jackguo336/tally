from peewee import CharField, ForeignKeyField, DateTimeField, IntegerField

from .base import BaseModel
from .user import User


class Activity(BaseModel):
    id = CharField(primary_key=True)
    user = ForeignKeyField(User, backref="activities")
    start_time = DateTimeField()
    elapsed_seconds = IntegerField()
    moving_seconds = IntegerField(null=True)
    title = CharField()
    workout_type = CharField()

    def as_dict(self):
        return {
            "id": self.id,
            "user": self.user,
            "start_time": self.start_time,
            "elapsed_seconds": self.elapsed_seconds,
            "moving_seconds": self.moving_seconds,
            "title": self.title,
            "workout_type": self.workout_type,
        }

    def __str__(self):
        return (
            f"Activity("
            f"id={self.id}, "
            f"user={self.user}, "
            f"start_time={self.start_time}, "
            f"elapsed_seconds={self.elapsed_seconds}, "
            f"moving_seconds={self.moving_seconds}, "
            f"title={self.title}, "
            f"workout_type={self.workout_type})"
        )

    def __repr__(self):
        return self.__str__()
