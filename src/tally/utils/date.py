import datetime
from typing import List
import pytz
import questionary


def date_validator(date: str) -> str | bool:
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Date must be valid and in the format YYYY-MM-DD"
    return True


def get_start_of_day(date: datetime.date, time_zone: str) -> datetime.datetime:
    date_with_time = datetime.datetime.combine(date, datetime.datetime.min.time())
    return pytz.timezone(time_zone).localize(date_with_time)


def get_previous_day(date: datetime.date) -> datetime.date:
    return date - datetime.timedelta(days=1)


def get_file_timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def prompt_date(message: str, defaultDate: datetime.date | None) -> datetime.date | None:
    date = questionary.text(
        message,
        validate=date_validator,
        default=defaultDate.strftime("%Y-%m-%d") if defaultDate else "",
    ).ask()
    if not date:
        return None

    return datetime.datetime.strptime(date, "%Y-%m-%d").date()
