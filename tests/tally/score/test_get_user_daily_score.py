import datetime
import pytest

from tally.actions.score.user_score import (
    get_user_daily_score,
)
from tally.actions.score.user_active_time import UserActiveTime
from tests.tally.mocks.mock_team import create_team
from tests.tally.mocks.mock_user import create_user


@pytest.fixture
def init_users_and_teams(mock_db):
    team = create_team(id="team1", name="Test Team")
    team.save(force_insert=True)
    create_user(id="user1", name="Test User", team=team.id).save(force_insert=True)
    create_user(id="user2", name="Test User 2", team=team.id).save(force_insert=True)
    yield


class TestGetUserDailyScore:
    def test_empty_user_active_times_list(self, mock_db):
        """Test with empty user active times list"""
        result = get_user_daily_score([])
        assert result == []

    def test_single_user_single_day_basic_points(self, mock_db, init_users_and_teams):
        """Test basic points calculation for single user on single day"""
        from tally.models.db import User

        user = User.get(User.id == "user1")

        # 30 minutes activity (1800 seconds) should give 5 points (threshold bonus)
        user_active_time = UserActiveTime(
            user=user, date=datetime.date(2023, 1, 15), active_seconds=1800
        )

        result = get_user_daily_score([user_active_time])

        assert len(result) == 1
        assert result[0].user.id == "user1"
        assert result[0].date == datetime.date(2023, 1, 15)
        assert result[0].points == 5  # 5 points for 30min threshold, no streak bonus

    def test_single_user_single_day_with_streak_bonus(
        self, mock_db, init_users_and_teams
    ):
        """Test that first day of activity gets streak 1 but no bonus points"""
        from tally.models.db import User

        user = User.get(User.id == "user1")

        user_active_time = UserActiveTime(
            user=user, date=datetime.date(2023, 1, 15), active_seconds=1800
        )

        result = get_user_daily_score([user_active_time])

        assert len(result) == 1
        assert result[0].points == 5  # No bonus for streak of 1

    def test_single_user_multiple_days_no_streak_break(
        self, mock_db, init_users_and_teams
    ):
        """Test consecutive days without streak break"""
        from tally.models.db import User

        user = User.get(User.id == "user1")

        user_active_times = [
            UserActiveTime(
                user=user, date=datetime.date(2023, 1, 15), active_seconds=1800
            ),
            UserActiveTime(
                user=user, date=datetime.date(2023, 1, 16), active_seconds=1800
            ),
            UserActiveTime(
                user=user, date=datetime.date(2023, 1, 17), active_seconds=1800
            ),
        ]

        result = get_user_daily_score(user_active_times)

        assert len(result) == 3

        # Day 1: streak=1, no bonus
        assert result[0].date == datetime.date(2023, 1, 15)
        assert result[0].points == 5  # 5 base points, no bonus

        # Day 2: streak=2, no bonus
        assert result[1].date == datetime.date(2023, 1, 16)
        assert result[1].points == 5  # 5 base points, no bonus

        # Day 3: streak=3, no bonus
        assert result[2].date == datetime.date(2023, 1, 17)
        assert result[2].points == 5  # 5 base points, no bonus

    def test_single_user_7_day_streak_gets_bonus(self, mock_db, init_users_and_teams):
        """Test that user gets bonus points on 7th consecutive day"""
        from tally.models.db import User

        user = User.get(User.id == "user1")

        user_active_times = []
        for day in range(1, 8):  # 7 consecutive days
            user_active_times.append(
                UserActiveTime(
                    user=user,
                    date=datetime.date(2023, 1, day),
                    active_seconds=1800,  # 30 minutes
                )
            )

        result = get_user_daily_score(user_active_times)

        assert len(result) == 7

        # First 6 days should have no bonus
        for i in range(6):
            assert result[i].points == 5  # 5 base points, no bonus

        # 7th day should have bonus
        assert result[6].date == datetime.date(2023, 1, 7)
        assert result[6].points == 10  # 5 base points + 5 bonus points

    def test_single_user_14_day_streak_gets_two_bonuses(
        self, mock_db, init_users_and_teams
    ):
        """Test that user gets bonus points on 7th and 14th consecutive days"""
        from tally.models.db import User

        user = User.get(User.id == "user1")

        user_active_times = []
        for day in range(1, 15):  # 14 consecutive days
            user_active_times.append(
                UserActiveTime(
                    user=user,
                    date=datetime.date(2023, 1, day),
                    active_seconds=1800,  # 30 minutes
                )
            )

        result = get_user_daily_score(user_active_times)

        assert len(result) == 14

        # 7th day should have bonus
        assert result[6].date == datetime.date(2023, 1, 7)
        assert result[6].points == 10  # 5 base points + 5 bonus points

        # 14th day should have bonus
        assert result[13].date == datetime.date(2023, 1, 14)
        assert result[13].points == 10  # 5 base points + 5 bonus points

        # Other days should have no bonus
        for i in [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12]:
            assert result[i].points == 5  # 5 base points, no bonus

    def test_single_user_streak_breaks_on_zero_activity(
        self, mock_db, init_users_and_teams
    ):
        """Test that streak breaks when user has 0 active seconds"""
        from tally.models.db import User

        user = User.get(User.id == "user1")

        user_active_times = [
            UserActiveTime(
                user=user, date=datetime.date(2023, 1, 1), active_seconds=1800
            ),
            UserActiveTime(
                user=user, date=datetime.date(2023, 1, 2), active_seconds=1800
            ),
            UserActiveTime(
                user=user, date=datetime.date(2023, 1, 3), active_seconds=0
            ),  # Breaks streak
            UserActiveTime(
                user=user, date=datetime.date(2023, 1, 4), active_seconds=1800
            ),
            UserActiveTime(
                user=user, date=datetime.date(2023, 1, 5), active_seconds=1800
            ),
        ]

        result = get_user_daily_score(user_active_times)

        assert len(result) == 5

        # Day 1: streak=1
        assert result[0].points == 5

        # Day 2: streak=2
        assert result[1].points == 5

        # Day 3: streak=0 (no activity), no points
        assert result[2].points == 0

        # Day 4: streak=1 (restart)
        assert result[3].points == 5

        # Day 5: streak=2
        assert result[4].points == 5

    def test_single_user_streak_breaks_and_reaches_7_again(
        self, mock_db, init_users_and_teams
    ):
        """Test that user can get bonus again after streak breaks and rebuilds"""
        from tally.models.db import User

        user = User.get(User.id == "user1")

        user_active_times = []

        # First 7 days
        for day in range(1, 8):
            user_active_times.append(
                UserActiveTime(
                    user=user, date=datetime.date(2023, 1, day), active_seconds=1800
                )
            )

        # Break streak on day 8
        user_active_times.append(
            UserActiveTime(user=user, date=datetime.date(2023, 1, 8), active_seconds=0)
        )

        # Another 7 days starting from day 9
        for day in range(9, 16):
            user_active_times.append(
                UserActiveTime(
                    user=user, date=datetime.date(2023, 1, day), active_seconds=1800
                )
            )

        result = get_user_daily_score(user_active_times)

        assert len(result) == 15

        # 7th day should have bonus
        assert result[6].date == datetime.date(2023, 1, 7)
        assert result[6].points == 10  # 5 base + 5 bonus

        # 8th day breaks streak
        assert result[7].date == datetime.date(2023, 1, 8)
        assert result[7].points == 0

        # 15th day (7th day of new streak) should have bonus
        assert result[14].date == datetime.date(2023, 1, 15)
        assert result[14].points == 10  # 5 base + 5 bonus

    def test_multiple_users_independent_streaks(self, mock_db, init_users_and_teams):
        """Test that different users have independent streak calculations"""
        from tally.models.db import User

        user1 = User.get(User.id == "user1")
        user2 = User.get(User.id == "user2")

        user_active_times = []

        # User1: 7 consecutive days
        for day in range(1, 8):
            user_active_times.append(
                UserActiveTime(
                    user=user1, date=datetime.date(2023, 1, day), active_seconds=1800
                )
            )

        # User2: only 3 days
        for day in range(1, 4):
            user_active_times.append(
                UserActiveTime(
                    user=user2, date=datetime.date(2023, 1, day), active_seconds=1800
                )
            )

        result = get_user_daily_score(user_active_times)

        assert len(result) == 10

        # Sort by user and date for predictable testing
        result.sort(key=lambda x: (x.user.id, x.date))

        # User1's 7th day should have bonus
        user1_results = [r for r in result if r.user.id == "user1"]
        assert len(user1_results) == 7
        assert user1_results[6].points == 10  # 5 base + 5 bonus

        # User2's days should have no bonus
        user2_results = [r for r in result if r.user.id == "user2"]
        assert len(user2_results) == 3
        for r in user2_results:
            assert r.points == 5  # Only base points

    def test_different_point_values_with_streaks(self, mock_db, init_users_and_teams):
        """Test that different activity durations give different base points but same bonus"""
        from tally.models.db import User

        user = User.get(User.id == "user1")

        user_active_times = []
        activity_durations = [1800, 3600, 7200]  # 30min, 60min, 120min

        # Create 7 days of activity with different durations
        for day in range(1, 8):
            duration = activity_durations[(day - 1) % 3]
            user_active_times.append(
                UserActiveTime(
                    user=user, date=datetime.date(2023, 1, day), active_seconds=duration
                )
            )

        result = get_user_daily_score(user_active_times)

        assert len(result) == 7

        # Expected points: 30min=5pts, 60min=8pts (1+5+2), 120min=10pts (2+5+2+1)
        expected_base_points = [5, 8, 10, 5, 8, 10, 5]

        for i in range(6):
            assert result[i].points == expected_base_points[i]

        # 7th day should have bonus added
        assert result[6].points == expected_base_points[6] + 5  # 5 base + 5 bonus = 10

    def test_unsorted_input_dates_are_handled_correctly(
        self, mock_db, init_users_and_teams
    ):
        """Test that unsorted input dates are sorted correctly for streak calculation"""
        from tally.models.db import User

        user = User.get(User.id == "user1")

        # Create dates out of order
        user_active_times = [
            UserActiveTime(
                user=user, date=datetime.date(2023, 1, 3), active_seconds=1800
            ),
            UserActiveTime(
                user=user, date=datetime.date(2023, 1, 1), active_seconds=1800
            ),
            UserActiveTime(
                user=user, date=datetime.date(2023, 1, 2), active_seconds=1800
            ),
        ]

        result = get_user_daily_score(user_active_times)

        assert len(result) == 3

        # Results should be in order of input, but streak calculated based on chronological order
        # Find results by date to verify streak calculation
        result_by_date = {r.date: r for r in result}

        # Each day should have correct streak-based calculation
        assert result_by_date[datetime.date(2023, 1, 1)].points == 5  # streak=1
        assert result_by_date[datetime.date(2023, 1, 2)].points == 5  # streak=2
        assert result_by_date[datetime.date(2023, 1, 3)].points == 5  # streak=3

    def test_multiple_users_unsorted_dates(self, mock_db, init_users_and_teams):
        """Test multiple users with unsorted dates"""
        from tally.models.db import User

        user1 = User.get(User.id == "user1")
        user2 = User.get(User.id == "user2")

        # Mixed users and dates
        user_active_times = [
            UserActiveTime(
                user=user2, date=datetime.date(2023, 1, 2), active_seconds=1800
            ),
            UserActiveTime(
                user=user1, date=datetime.date(2023, 1, 3), active_seconds=1800
            ),
            UserActiveTime(
                user=user2, date=datetime.date(2023, 1, 1), active_seconds=1800
            ),
            UserActiveTime(
                user=user1, date=datetime.date(2023, 1, 1), active_seconds=1800
            ),
        ]

        result = get_user_daily_score(user_active_times)

        assert len(result) == 4

        # All should have base points only (no 7-day streaks)
        for r in result:
            assert r.points == 5

    def test_gap_in_dates_breaks_streak(self, mock_db, init_users_and_teams):
        """Test that a gap in dates breaks the streak"""
        from tally.models.db import User

        user = User.get(User.id == "user1")

        user_active_times = [
            UserActiveTime(
                user=user, date=datetime.date(2023, 1, 1), active_seconds=1800
            ),
            UserActiveTime(
                user=user, date=datetime.date(2023, 1, 2), active_seconds=1800
            ),
            # Gap on Jan 3
            UserActiveTime(
                user=user, date=datetime.date(2023, 1, 4), active_seconds=1800
            ),
            UserActiveTime(
                user=user, date=datetime.date(2023, 1, 5), active_seconds=1800
            ),
        ]

        result = get_user_daily_score(user_active_times)

        assert len(result) == 4

        # Find results by date
        result_by_date = {r.date: r for r in result}

        # First two days build streak
        assert result_by_date[datetime.date(2023, 1, 1)].points == 5  # streak=1
        assert result_by_date[datetime.date(2023, 1, 2)].points == 5  # streak=2

        # After gap, streak restarts
        assert (
            result_by_date[datetime.date(2023, 1, 4)].points == 5
        )  # streak=1 (restarted)
        assert result_by_date[datetime.date(2023, 1, 5)].points == 5  # streak=2
