import datetime
from typing import List
import pytz


def date_validator(date: str) -> str | bool:
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Date must be valid and in the format YYYY-MM-DD"
    return True


def get_start_of_day(date: datetime.date, time_zone: str) -> datetime.datetime:
    date_with_time = datetime.datetime.combine(date, datetime.datetime.min.time())
    return pytz.timezone(time_zone).localize(date_with_time)


def get_end_of_day(date: datetime.date, time_zone: str) -> datetime.datetime:
    date_with_time = datetime.datetime.combine(date, datetime.datetime.max.time())
    return pytz.timezone(time_zone).localize(date_with_time)


def get_previous_day_date_str(date: str) -> str:
    return (
        datetime.datetime.strptime(date, "%Y-%m-%d") - datetime.timedelta(days=1)
    ).strftime("%Y-%m-%d")


def get_previous_day(date: datetime.date) -> datetime.date:
    return date - datetime.timedelta(days=1)


def get_dates_between(
    start_date: datetime.date, end_date: datetime.date
) -> List[datetime.date]:
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += datetime.timedelta(days=1)
    return dates
