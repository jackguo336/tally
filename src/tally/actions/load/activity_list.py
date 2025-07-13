from typing import List
import csv
from pydantic import BaseModel
from tally.utils.date import parse_duration


class ActivityRow(BaseModel):
    link: str
    user_link: str
    title: str
    workout_type: str
    date: str
    active_time: str

    def get_activity_id(self) -> str:
        return self.link.split("/")[-1]

    def get_user_id(self) -> str:
        return self.user_link.split("/")[-1]

    def get_active_seconds(self) -> int:
        return parse_duration(self.active_time)

    def is_incomplete(self) -> bool:
        return (
            not self.link
            or not self.user_link
            or not self.title
            or not self.workout_type
            or not self.date
            or not self.active_time
        )


def parse_activity_list(activity_list_path: str) -> List[ActivityRow]:
    with open(activity_list_path, "r") as file:
        reader = csv.DictReader(file)
        activity_list = []
        for row in reader:
            activity_list.append(ActivityRow(**row))

    return activity_list
