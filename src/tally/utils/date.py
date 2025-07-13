import datetime
import pytz
import questionary
import re


ONE_HOUR_IN_SECONDS = 3600
ONE_MINUTE_IN_SECONDS = 60


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


def prompt_date(
    message: str, defaultDate: datetime.date | None
) -> datetime.date | None:
    date = questionary.text(
        message,
        validate=date_validator,
        default=defaultDate.strftime("%Y-%m-%d") if defaultDate else "",
    ).ask()
    if not date:
        return None

    return datetime.datetime.strptime(date, "%Y-%m-%d").date()


def get_local_date(date: datetime.date, time_zone: str) -> datetime.date:
    return date.astimezone(pytz.timezone(time_zone)).date()


def format_duration(seconds: int) -> str:
    hours = seconds // ONE_HOUR_IN_SECONDS
    minutes = (seconds % ONE_HOUR_IN_SECONDS) // ONE_MINUTE_IN_SECONDS
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def parse_duration(duration: str) -> int:
    """
    Converts a duration string in the format "1h 15m" to seconds.
    """

    duration_regex = r"(?:(\d+)\s*h\s*)?(\d+)\s*m"
    match = re.search(duration_regex, duration.strip())
    if match:
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2))
        return hours * ONE_HOUR_IN_SECONDS + minutes * ONE_MINUTE_IN_SECONDS
    else:
        raise ValueError(f"Invalid duration format: {duration}")
