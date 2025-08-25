from tally.actions.score.point_system import calculate_team_bonus_points


class TestCalculateTeamBonusPoints:
    """Test cases for calculate_team_bonus_points function."""

    def test_zero_active_users_zero_total_users_returns_zero_points(self):
        """Test that teams with no members do not receive bonus points."""
        result = calculate_team_bonus_points(0, 0)
        assert result == 0

    def test_zero_active_users_with_total_users_returns_zero_points(self):
        """Test that zero active users with total users returns zero points."""
        result = calculate_team_bonus_points(0, 5)
        assert result == 0

    def test_some_active_users_returns_zero_points(self):
        """Test that partial team activity returns zero bonus points."""
        result = calculate_team_bonus_points(1, 2)
        assert result == 0

    def test_all_users_active_returns_bonus_points(self):
        """Test that full team activity returns bonus points for teams with members."""
        # Test single user team
        result = calculate_team_bonus_points(1, 1)
        assert result == 5
        
        # Test larger team
        result = calculate_team_bonus_points(5, 5)
        assert result == 5
