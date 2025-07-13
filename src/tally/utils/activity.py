from tally.models.activity import Activity


MOVING_TIME_ACTIVITY_TYPES = ["Walk", "Run", "EBikeRide", "Ride", "Hike"]


def get_activity_active_seconds(activity: Activity) -> int:
    """
    The time spent in the activity that counts when calculating the score.

    For certain activities defined in MOVING_TIME_ACTIVITY_TYPES, the moving
    time is preferred over active time because Strava uses the auto-pause
    feature to prevent over-tracking when the user forgets to end the activity.
    """

    if (
        activity.workout_type in MOVING_TIME_ACTIVITY_TYPES
        and activity.moving_seconds is not None
    ):
        return activity.moving_seconds
    return activity.elapsed_seconds


def get_activity_link(activity: Activity) -> str:
    return f"https://www.strava.com/activities/{activity.id}"
