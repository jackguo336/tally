def calculate_user_points(active_seconds: int) -> int:
    """
    Assign points for a specific day based on how long the user was active for
    that day. Points increase with active time in 30 minute/1 hour increments.
    More points are awarded towards for the first few threshold 30 minutes, 60
    minutes and 120 minutes.

    :param active_seconds: Total active time in seconds for a specific day.

    :return: Points for the specific day.
    """
    one_minute_in_seconds = 60
    one_hour_in_minutes = 60
    point_map = [
        {"minutes": 30, "points": 5},
        {"minutes": 60, "points": 2},
        {"minutes": 120, "points": 1},
    ]

    active_minutes = active_seconds / one_minute_in_seconds
    # Base points: 1 point per hour
    points = active_minutes // one_hour_in_minutes
    # Additional points based on time thresholds
    for point_map in point_map:
        if active_minutes >= point_map["minutes"]:
            points += point_map["points"]
    return points


def calculate_user_bonus_points(streak: int) -> int:
    """
    Reward users with 5 bonus points for being active every 7 consecutive days.

    :param streak: The number of consecutive days the user has been active.

    :return: Bonus points for the user.
    """
    bonus_points = 5
    bonus_points_streak_interval = 7
    return (
        bonus_points if streak > 0 and streak % bonus_points_streak_interval == 0 else 0
    )


def calculate_team_bonus_points(active_user_count: int, total_user_count: int) -> int:
    """
    Reward teams with 5 bonus points if all users in the team have been active
    for a specific day. Teams with no members do not receive bonus points.

    :param active_user_count: Number of active users in the team.
    :param total_user_count: Total number of users in the team.

    :return: Bonus points for the team.
    """
    bonus_points = 5
    return (
        bonus_points
        if total_user_count > 0 and active_user_count == total_user_count
        else 0
    )
