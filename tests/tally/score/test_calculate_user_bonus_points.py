from tally.actions.score.point_system import calculate_user_bonus_points


class TestCalculateUserBonusPoints:
    """Test cases for calculate_user_bonus_points function."""

    def test_zero_streak_returns_zero_points(self):
        """Test that a streak of 0 returns 0 bonus points."""
        result = calculate_user_bonus_points(0)
        assert result == 0

    def test_negative_streak_returns_zero_points(self):
        """Test that negative streaks return 0 bonus points."""
        result = calculate_user_bonus_points(-1)
        assert result == 0
        
        result = calculate_user_bonus_points(-7)
        assert result == 0

    def test_streak_less_than_seven_returns_zero_points(self):
        """Test that streaks less than 7 return 0 bonus points."""
        for streak in range(1, 7):
            result = calculate_user_bonus_points(streak)
            assert result == 0, f"Streak {streak} should return 0 points"

    def test_streak_of_seven_returns_bonus_points(self):
        """Test that a streak of exactly 7 days returns 5 bonus points."""
        result = calculate_user_bonus_points(7)
        assert result == 5

    def test_streak_multiple_of_seven_returns_bonus_points(self):
        """Test that streaks that are multiples of 7 return bonus points."""
        test_cases = [
            (14, 5),   # 2 weeks
            (21, 5),   # 3 weeks
            (28, 5),   # 4 weeks
            (35, 5),   # 5 weeks
            (70, 5),   # 10 weeks
        ]
        
        for streak, expected_points in test_cases:
            result = calculate_user_bonus_points(streak)
            assert result == expected_points, f"Streak {streak} should return {expected_points} points"

    def test_streak_not_multiple_of_seven_returns_zero_points(self):
        """Test that streaks not divisible by 7 return 0 bonus points."""
        test_cases = [0, 1, 6, 8, 9, 13, 15, 20, 22, 29, 50, 71]
        
        for streak in test_cases:
            result = calculate_user_bonus_points(streak)
            assert result == 0, f"Streak {streak} should return 0 points"
