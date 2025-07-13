import datetime

from tally.actions.score.user_active_time import (
    get_user_active_time,
    MOVING_TIME_ACTIVITY_TYPES,
)
from tally.actions.score.score_config import ScoreConfig


class MockUser:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name


class MockActivity:
    def __init__(
        self,
        id: str,
        user: MockUser,
        start_time: str,
        elapsed_seconds: int,
        workout_type: str,
        moving_seconds: int = None,
    ):
        self.id = id
        self.user = user
        self.start_time = start_time
        self.elapsed_seconds = elapsed_seconds
        self.workout_type = workout_type
        self.moving_seconds = moving_seconds


class TestGetUserActiveTime:
    def test_empty_activities_list(self):
        """Test with empty activities list"""
        config = ScoreConfig(
            score_start_date=datetime.date(2023, 1, 1),
            score_end_date=datetime.date(2023, 1, 31),
            time_zone="UTC",
        )
        
        result = get_user_active_time([], config)
        
        assert result == []

    def test_single_activity_within_date_range(self):
        """Test with single activity within date range"""
        user = MockUser("user1", "Test User")
        activity = MockActivity(
            id="activity1",
            user=user,
            start_time="2023-01-15T10:00:00+00:00",
            elapsed_seconds=3600,
            workout_type="Other",
        )
        config = ScoreConfig(
            score_start_date=datetime.date(2023, 1, 1),
            score_end_date=datetime.date(2023, 1, 31),
            time_zone="UTC",
        )
        
        result = get_user_active_time([activity], config)
        
        assert len(result) == 1
        assert result[0].user == user
        assert result[0].date == datetime.date(2023, 1, 15)
        assert result[0].active_seconds == 3600

    def test_activity_before_start_date_filtered_out(self):
        """Test that activities before start date are filtered out"""
        user = MockUser("user1", "Test User")
        activity = MockActivity(
            id="activity1",
            user=user,
            start_time="2022-12-31T10:00:00+00:00",
            elapsed_seconds=3600,
            workout_type="Other",
        )
        config = ScoreConfig(
            score_start_date=datetime.date(2023, 1, 1),
            score_end_date=datetime.date(2023, 1, 31),
            time_zone="UTC",
        )
        
        result = get_user_active_time([activity], config)
        
        assert result == []

    def test_activity_after_end_date_filtered_out(self):
        """Test that activities after end date are filtered out"""
        user = MockUser("user1", "Test User")
        activity = MockActivity(
            id="activity1",
            user=user,
            start_time="2023-02-01T10:00:00+00:00",
            elapsed_seconds=3600,
            workout_type="Other",
        )
        config = ScoreConfig(
            score_start_date=datetime.date(2023, 1, 1),
            score_end_date=datetime.date(2023, 1, 31),
            time_zone="UTC",
        )
        
        result = get_user_active_time([activity], config)
        
        assert result == []

    def test_timezone_conversion(self):
        """Test that activities are correctly converted to config timezone"""
        user = MockUser("user1", "Test User")
        # Activity starts at 23:00 UTC on Jan 15, which is 18:00 EST on Jan 15
        activity = MockActivity(
            id="activity1",
            user=user,
            start_time="2023-01-15T23:00:00+00:00",  # UTC timezone-aware
            elapsed_seconds=3600,
            workout_type="Other",
        )
        config = ScoreConfig(
            score_start_date=datetime.date(2023, 1, 1),
            score_end_date=datetime.date(2023, 1, 31),
            time_zone="US/Eastern",
        )
        
        result = get_user_active_time([activity], config)
        
        assert len(result) == 1
        assert result[0].date == datetime.date(2023, 1, 15)  # Still Jan 15 in EST

    def test_timezone_conversion_crosses_date_boundary(self):
        """Test timezone conversion when it crosses date boundary"""
        user = MockUser("user1", "Test User")
        # Activity starts at 02:00 UTC on Jan 16, which is 21:00 EST on Jan 15
        activity = MockActivity(
            id="activity1",
            user=user,
            start_time="2023-01-16T02:00:00+00:00",  # UTC timezone-aware
            elapsed_seconds=3600,
            workout_type="Other",
        )
        config = ScoreConfig(
            score_start_date=datetime.date(2023, 1, 1),
            score_end_date=datetime.date(2023, 1, 31),
            time_zone="US/Eastern",
        )
        
        result = get_user_active_time([activity], config)
        
        assert len(result) == 1
        assert result[0].date == datetime.date(2023, 1, 15)  # Jan 15 in EST

    def test_timezone_conversion_america_los_angeles_boundary(self):
        """Test timezone conversion with America/Los_Angeles timezone crossing date boundary"""
        user = MockUser("user1", "Test User")
        # Activity starts at 08:00 UTC on Jan 16, which is 00:00 PST on Jan 16
        # (PST is UTC-8, so 8 hours earlier)
        activity = MockActivity(
            id="activity1",
            user=user,
            start_time="2023-01-16T08:00:00+00:00",  # UTC timezone-aware
            elapsed_seconds=3600,
            workout_type="Other",
        )
        config = ScoreConfig(
            score_start_date=datetime.date(2023, 1, 1),
            score_end_date=datetime.date(2023, 1, 31),
            time_zone="America/Los_Angeles",
        )
        
        result = get_user_active_time([activity], config)
        
        assert len(result) == 1
        assert result[0].date == datetime.date(2023, 1, 16)  # Still Jan 16 in PST
        
        # Test case where it crosses to previous day
        activity2 = MockActivity(
            id="activity2",
            user=user,
            start_time="2023-01-16T07:00:00+00:00",  # UTC timezone-aware
            elapsed_seconds=1800,
            workout_type="Other",
        )
        
        result2 = get_user_active_time([activity2], config)
        
        assert len(result2) == 1
        assert result2[0].date == datetime.date(2023, 1, 15)  # Jan 15 in PST (7 UTC = 23 PST previous day)

    def test_moving_time_activity_types_use_moving_seconds(self):
        """Test that moving time activity types use moving_seconds when available"""
        user = MockUser("user1", "Test User")
        
        for activity_type in MOVING_TIME_ACTIVITY_TYPES:
            activity = MockActivity(
                id=f"activity_{activity_type}",
                user=user,
                start_time="2023-01-15T10:00:00+00:00",
                elapsed_seconds=3600,
                workout_type=activity_type,
                moving_seconds=1800,  # 30 minutes moving time
            )
            config = ScoreConfig(
                score_start_date=datetime.date(2023, 1, 1),
                score_end_date=datetime.date(2023, 1, 31),
                time_zone="UTC",
            )
            
            result = get_user_active_time([activity], config)
            
            assert len(result) == 1
            assert result[0].active_seconds == 1800  # Uses moving_seconds

    def test_moving_time_activity_with_null_moving_seconds_uses_elapsed(self):
        """Test that moving time activities with null moving_seconds use elapsed_seconds"""
        user = MockUser("user1", "Test User")
        activity = MockActivity(
            id="activity1",
            user=user,
            start_time="2023-01-15T10:00:00+00:00",
            elapsed_seconds=3600,
            workout_type="Run",
            moving_seconds=None,
        )
        config = ScoreConfig(
            score_start_date=datetime.date(2023, 1, 1),
            score_end_date=datetime.date(2023, 1, 31),
            time_zone="UTC",
        )
        
        result = get_user_active_time([activity], config)
        
        assert len(result) == 1
        assert result[0].active_seconds == 3600  # Uses elapsed_seconds

    def test_non_moving_time_activity_uses_elapsed_seconds(self):
        """Test that non-moving time activities use elapsed_seconds"""
        user = MockUser("user1", "Test User")
        activity = MockActivity(
            id="activity1",
            user=user,
            start_time="2023-01-15T10:00:00+00:00",
            elapsed_seconds=3600,
            workout_type="Yoga",
            moving_seconds=1800,
        )
        config = ScoreConfig(
            score_start_date=datetime.date(2023, 1, 1),
            score_end_date=datetime.date(2023, 1, 31),
            time_zone="UTC",
        )
        
        result = get_user_active_time([activity], config)
        
        assert len(result) == 1
        assert result[0].active_seconds == 3600  # Uses elapsed_seconds

    def test_multiple_activities_same_user_same_date_accumulated(self):
        """Test that multiple activities for same user on same date are accumulated"""
        user = MockUser("user1", "Test User")
        activity1 = MockActivity(
            id="activity1",
            user=user,
            start_time="2023-01-15T10:00:00+00:00",
            elapsed_seconds=1800,
            workout_type="Run",
            moving_seconds=1500,
        )
        activity2 = MockActivity(
            id="activity2",
            user=user,
            start_time="2023-01-15T16:00:00+00:00",
            elapsed_seconds=2400,
            workout_type="Walk",
            moving_seconds=2000,
        )
        config = ScoreConfig(
            score_start_date=datetime.date(2023, 1, 1),
            score_end_date=datetime.date(2023, 1, 31),
            time_zone="UTC",
        )
        
        result = get_user_active_time([activity1, activity2], config)
        
        assert len(result) == 1
        assert result[0].user == user
        assert result[0].date == datetime.date(2023, 1, 15)
        assert result[0].active_seconds == 3500  # 1500 + 2000

    def test_multiple_activities_same_user_different_dates(self):
        """Test that activities for same user on different dates create separate entries"""
        user = MockUser("user1", "Test User")
        activity1 = MockActivity(
            id="activity1",
            user=user,
            start_time="2023-01-15T10:00:00+00:00",
            elapsed_seconds=1800,
            workout_type="Other",
        )
        activity2 = MockActivity(
            id="activity2",
            user=user,
            start_time="2023-01-16T10:00:00+00:00",
            elapsed_seconds=2400,
            workout_type="Other",
        )
        config = ScoreConfig(
            score_start_date=datetime.date(2023, 1, 1),
            score_end_date=datetime.date(2023, 1, 31),
            time_zone="UTC",
        )
        
        result = get_user_active_time([activity1, activity2], config)
        
        assert len(result) == 2
        
        # Sort by date for consistent testing
        result.sort(key=lambda x: x.date)
        
        assert result[0].user == user
        assert result[0].date == datetime.date(2023, 1, 15)
        assert result[0].active_seconds == 1800
        
        assert result[1].user == user
        assert result[1].date == datetime.date(2023, 1, 16)
        assert result[1].active_seconds == 2400

    def test_multiple_users_same_date(self):
        """Test that activities for different users on same date create separate entries"""
        user1 = MockUser("user1", "User 1")
        user2 = MockUser("user2", "User 2")
        activity1 = MockActivity(
            id="activity1",
            user=user1,
            start_time="2023-01-15T10:00:00+00:00",
            elapsed_seconds=1800,
            workout_type="Other",
        )
        activity2 = MockActivity(
            id="activity2",
            user=user2,
            start_time="2023-01-15T10:00:00+00:00",
            elapsed_seconds=2400,
            workout_type="Other",
        )
        config = ScoreConfig(
            score_start_date=datetime.date(2023, 1, 1),
            score_end_date=datetime.date(2023, 1, 31),
            time_zone="UTC",
        )
        
        result = get_user_active_time([activity1, activity2], config)
        
        assert len(result) == 2
        
        # Sort by user id for consistent testing
        result.sort(key=lambda x: x.user.id)
        
        assert result[0].user == user1
        assert result[0].date == datetime.date(2023, 1, 15)
        assert result[0].active_seconds == 1800
        
        assert result[1].user == user2
        assert result[1].date == datetime.date(2023, 1, 15)
        assert result[1].active_seconds == 2400

    def test_complex_scenario_multiple_users_dates_activities(self):
        """Test complex scenario with multiple users, dates, and activities"""
        user1 = MockUser("user1", "User 1")
        user2 = MockUser("user2", "User 2")
        
        activities = [
            # User 1 - Jan 15 - 2 activities
            MockActivity("act1", user1, "2023-01-15T10:00:00+00:00", 1800, "Run", 1500),
            MockActivity("act2", user1, "2023-01-15T16:00:00+00:00", 2400, "Walk", 2000),
            # User 1 - Jan 16 - 1 activity
            MockActivity("act3", user1, "2023-01-16T10:00:00+00:00", 3600, "Yoga"),
            # User 2 - Jan 15 - 1 activity
            MockActivity("act4", user2, "2023-01-15T10:00:00+00:00", 2700, "Ride", 2500),
            # User 2 - Jan 17 - 1 activity
            MockActivity("act5", user2, "2023-01-17T10:00:00+00:00", 1800, "Other"),
            # Activity outside date range (should be filtered)
            MockActivity("act6", user1, "2023-02-01T10:00:00+00:00", 3600, "Other"),
        ]
        
        config = ScoreConfig(
            score_start_date=datetime.date(2023, 1, 1),
            score_end_date=datetime.date(2023, 1, 31),
            time_zone="UTC",
        )
        
        result = get_user_active_time(activities, config)
        
        assert len(result) == 4  # 5 activities minus 1 filtered out
        
        # Sort for consistent testing
        result.sort(key=lambda x: (x.user.id, x.date))
        
        # User 1 - Jan 15 (combined activities)
        assert result[0].user == user1
        assert result[0].date == datetime.date(2023, 1, 15)
        assert result[0].active_seconds == 3500  # 1500 + 2000
        
        # User 1 - Jan 16
        assert result[1].user == user1
        assert result[1].date == datetime.date(2023, 1, 16)
        assert result[1].active_seconds == 3600
        
        # User 2 - Jan 15
        assert result[2].user == user2
        assert result[2].date == datetime.date(2023, 1, 15)
        assert result[2].active_seconds == 2500  # Uses moving_seconds for "Ride"
        
        # User 2 - Jan 17
        assert result[3].user == user2
        assert result[3].date == datetime.date(2023, 1, 17)
        assert result[3].active_seconds == 1800

    def test_activity_on_boundary_dates(self):
        """Test activities on start and end boundary dates are included"""
        user = MockUser("user1", "Test User")
        activity_start = MockActivity(
            id="activity1",
            user=user,
            start_time="2023-01-01T10:00:00+00:00",
            elapsed_seconds=1800,
            workout_type="Other",
        )
        activity_end = MockActivity(
            id="activity2",
            user=user,
            start_time="2023-01-31T10:00:00+00:00",
            elapsed_seconds=2400,
            workout_type="Other",
        )
        config = ScoreConfig(
            score_start_date=datetime.date(2023, 1, 1),
            score_end_date=datetime.date(2023, 1, 31),
            time_zone="UTC",
        )
        
        result = get_user_active_time([activity_start, activity_end], config)
        
        assert len(result) == 2
        
        # Sort by date for consistent testing
        result.sort(key=lambda x: x.date)
        
        assert result[0].date == datetime.date(2023, 1, 1)
        assert result[0].active_seconds == 1800
        
        assert result[1].date == datetime.date(2023, 1, 31)
        assert result[1].active_seconds == 2400
