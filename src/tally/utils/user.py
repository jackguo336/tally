from tally.models.user import User


def get_user_link(user: User) -> str:
    return f"https://www.strava.com/athletes/{user.id}"
