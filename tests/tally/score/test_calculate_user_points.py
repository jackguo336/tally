import pytest

from tally.actions.score.point_system import calculate_user_points


class TestCalculateUserPoints:
    def test_zero_activity(self):
        """Test that zero active time returns zero points"""
        assert calculate_user_points(0) == 0

    def test_below_30_minute_threshold(self):
        """Test activity below 30 minutes gets no bonus points"""
        # 15 minutes
        assert calculate_user_points(15 * 60) == 0

        # Just below 30 minutes
        assert calculate_user_points(29 * 60 + 59) == 0

    def test_30_minute_threshold(self):
        """Test 30-minute threshold gives 5 bonus points"""
        # Exactly 30 minutes
        assert calculate_user_points(30 * 60) == 5

        # Just above 30 minutes
        assert calculate_user_points(30 * 60 + 1) == 5

    def test_between_30_and_60_minutes(self):
        """Test activity between 30 and 60 minutes"""
        # 45 minutes
        assert calculate_user_points(45 * 60) == 5

    def test_just_below_60_minute_threshold(self):
        """Test just below 60-minute threshold"""
        assert calculate_user_points(59 * 60 + 59) == 5

    def test_60_minute_threshold(self):
        """Test 60-minute threshold gives additional 2 bonus points"""
        # Exactly 60 minutes: 1 base + 5 (30min) + 2 (60min) = 8
        assert calculate_user_points(60 * 60) == 8

        # Just above 60 minutes
        assert calculate_user_points(60 * 60 + 1) == 8

    def test_between_60_and_120_minutes(self):
        """Test activity between 60 and 120 minutes"""
        # 90 minutes: 1 base + 5 (30min) + 2 (60min) = 8
        assert calculate_user_points(90 * 60) == 8

    def test_just_below_120_minute_threshold(self):
        """Test just below 120-minute threshold"""
        assert calculate_user_points(119 * 60 + 59) == 8

    def test_120_minute_threshold(self):
        """Test 120-minute threshold gives additional 1 bonus point"""
        # Exactly 120 minutes: 2 base + 5 (30min) + 2 (60min) + 1 (120min) = 10
        assert calculate_user_points(120 * 60) == 10

        # Just above 120 minutes
        assert calculate_user_points(120 * 60 + 1) == 10

    def test_above_120_minutes_only_base_points(self):
        """Test that above 120 minutes, only base points increase"""
        # 150 minutes: 2 base + 5 (30min) + 2 (60min) + 1 (120min) = 10
        assert calculate_user_points(150 * 60) == 10

        # 180 minutes: 3 base + 5 (30min) + 2 (60min) + 1 (120min) = 11
        assert calculate_user_points(180 * 60) == 11

        # 240 minutes: 4 base + 5 (30min) + 2 (60min) + 1 (120min) = 12
        assert calculate_user_points(240 * 60) == 12

    def test_all_requested_durations(self):
        """Test all specifically requested durations"""
        expected_points = {
            15: 0,  # Below first threshold
            30: 5,  # First threshold: 0 base + 5 bonus
            45: 5,  # Between first and second threshold: 0 base + 5 bonus
            60: 8,  # Second threshold: 1 base + 5 + 2 bonus
            90: 8,  # Between second and third threshold: 1 base + 5 + 2 bonus
            120: 10,  # Third threshold: 2 base + 5 + 2 + 1 bonus
            150: 10,  # Above all thresholds: 2 base + 5 + 2 + 1 bonus
            180: 11,  # Above all thresholds: 3 base + 5 + 2 + 1 bonus
            240: 12,  # Above all thresholds: 4 base + 5 + 2 + 1 bonus
        }

        for minutes, expected in expected_points.items():
            seconds = minutes * 60
            actual = calculate_user_points(seconds)
            assert (
                actual == expected
            ), f"Expected {expected} points for {minutes} minutes, got {actual}"

    def test_threshold_boundaries(self):
        """Test exact threshold boundaries"""
        # 30-minute threshold
        assert calculate_user_points(29 * 60 + 59) == 0  # Just below
        assert calculate_user_points(30 * 60) == 5  # Exactly at
        assert calculate_user_points(30 * 60 + 1) == 5  # Just above

        # 60-minute threshold
        assert calculate_user_points(59 * 60 + 59) == 5  # Just below
        assert calculate_user_points(60 * 60) == 8  # Exactly at
        assert calculate_user_points(60 * 60 + 1) == 8  # Just above

        # 120-minute threshold
        assert calculate_user_points(119 * 60 + 59) == 8  # Just below
        assert calculate_user_points(120 * 60) == 10  # Exactly at
        assert calculate_user_points(120 * 60 + 1) == 10  # Just above

    def test_base_points_calculation(self):
        """Test that base points are calculated as 1 point per hour"""
        # Test various hour marks
        assert calculate_user_points(1 * 60 * 60) == 8  # 1 hour: 1 base + 5 + 2 = 8
        assert (
            calculate_user_points(2 * 60 * 60) == 10
        )  # 2 hours: 2 base + 5 + 2 + 1 = 10
        assert (
            calculate_user_points(3 * 60 * 60) == 11
        )  # 3 hours: 3 base + 5 + 2 + 1 = 11
        assert (
            calculate_user_points(4 * 60 * 60) == 12
        )  # 4 hours: 4 base + 5 + 2 + 1 = 12
        assert (
            calculate_user_points(5 * 60 * 60) == 13
        )  # 5 hours: 5 base + 5 + 2 + 1 = 13

    def test_partial_hours(self):
        """Test that partial hours don't count for base points"""
        # 1.5 hours should still only count as 1 hour for base points
        assert calculate_user_points(90 * 60) == 8  # 1 base + 5 + 2 = 8

        # 2.9 hours should still only count as 2 hours for base points
        assert calculate_user_points(174 * 60) == 10  # 2 base + 5 + 2 + 1 = 10

    def test_edge_case_very_long_activity(self):
        """Test very long activity periods"""
        # 10 hours
        ten_hours = 10 * 60 * 60
        expected = 10 + 5 + 2 + 1  # 10 base + bonuses = 18
        assert calculate_user_points(ten_hours) == expected

        # 24 hours
        twenty_four_hours = 24 * 60 * 60
        expected = 24 + 5 + 2 + 1  # 24 base + bonuses = 32
        assert calculate_user_points(twenty_four_hours) == expected

    def test_no_score_activity_periods(self):
        """Test no score activity periods"""
        assert calculate_user_points(1) == 0  # 1 second
        assert calculate_user_points(59) == 0  # 59 seconds
        assert calculate_user_points(60) == 0  # 1 minute
        assert calculate_user_points(5 * 60) == 0  # 5 minutes
        assert calculate_user_points(29 * 60) == 0  # 29 minutes

    def test_return_type_is_numeric(self):
        """Test that the function returns a numeric type"""
        result = calculate_user_points(1800)  # 30 minutes
        assert isinstance(result, (int, float))
        assert result == 5
