import pytest
from datetime import date
from tally.actions.score.team_score import get_team_daily_score
from tally.actions.score.user_score import UserDailyScore
from tests.tally.mocks.mock_user import create_user
from tests.tally.mocks.mock_team import create_team


@pytest.fixture
def init_teams_and_users(mock_db):
    """Create test teams and users for database tests"""
    # Create teams
    team1 = create_team(id="team1", name="Team Alpha")
    team1.save(force_insert=True)
    
    team2 = create_team(id="team2", name="Team Beta")
    team2.save(force_insert=True)
    
    # Create users for team1
    user1 = create_user(id="user1", name="Alice", team="team1")
    user1.save(force_insert=True)
    
    user2 = create_user(id="user2", name="Bob", team="team1")
    user2.save(force_insert=True)
    
    # Create users for team2
    user3 = create_user(id="user3", name="Charlie", team="team2")
    user3.save(force_insert=True)
    
    user4 = create_user(id="user4", name="Diana", team="team2")
    user4.save(force_insert=True)
    
    yield


class TestGetTeamDailyScore:
    """Test cases for get_team_daily_score function."""
    
    def test_empty_user_daily_scores_returns_empty_list(self, mock_db, init_teams_and_users):
        """Test that empty user daily scores list returns empty team scores list"""
        from tally.models.db import User
        
        users = list(User.select())
        result = get_team_daily_score([], users)
        
        assert result == []
    
    def test_single_team_single_user_single_date(self, mock_db, init_teams_and_users):
        """Test basic functionality with single team, single user, single date"""
        from tally.models.db import User
        
        user1 = User.get(User.id == "user1")
        users = [user1]
        
        user_daily_score = UserDailyScore(
            user=user1,
            date=date(2023, 1, 15),
            points=10
        )
        
        result = get_team_daily_score([user_daily_score], users)
        
        assert len(result) == 1
        team_score = result[0]
        assert team_score.team.id == "team1"
        assert team_score.date == date(2023, 1, 15)
        assert len(team_score.user_scores) == 1
        assert team_score.user_scores[0].points == 10
        assert team_score.users == users
    
    def test_single_team_multiple_users_same_date(self, mock_db, init_teams_and_users):
        """Test single team with multiple users on the same date"""
        from tally.models.db import User
        
        user1 = User.get(User.id == "user1")
        user2 = User.get(User.id == "user2")
        users = [user1, user2]
        
        user_daily_scores = [
            UserDailyScore(user=user1, date=date(2023, 1, 15), points=10),
            UserDailyScore(user=user2, date=date(2023, 1, 15), points=15)
        ]
        
        result = get_team_daily_score(user_daily_scores, users)
        
        assert len(result) == 1
        team_score = result[0]
        assert team_score.team.id == "team1"
        assert team_score.date == date(2023, 1, 15)
        assert len(team_score.user_scores) == 2
        
        # Check that both user scores are included
        user_points = [score.points for score in team_score.user_scores]
        assert 10 in user_points
        assert 15 in user_points
    
    def test_multiple_teams_same_date(self, mock_db, init_teams_and_users):
        """Test multiple teams with users on the same date"""
        from tally.models.db import User
        
        user1 = User.get(User.id == "user1")
        user3 = User.get(User.id == "user3")
        users = [user1, user3]
        
        user_daily_scores = [
            UserDailyScore(user=user1, date=date(2023, 1, 15), points=10),
            UserDailyScore(user=user3, date=date(2023, 1, 15), points=20)
        ]
        
        result = get_team_daily_score(user_daily_scores, users)
        
        assert len(result) == 2
        
        # Sort results by team id for consistent testing
        result.sort(key=lambda x: x.team.id)
        
        # Check team1 score
        team1_score = result[0]
        assert team1_score.team.id == "team1"
        assert team1_score.date == date(2023, 1, 15)
        assert len(team1_score.user_scores) == 1
        assert team1_score.user_scores[0].points == 10
        
        # Check team2 score
        team2_score = result[1]
        assert team2_score.team.id == "team2"
        assert team2_score.date == date(2023, 1, 15)
        assert len(team2_score.user_scores) == 1
        assert team2_score.user_scores[0].points == 20
    
    def test_same_team_multiple_dates(self, mock_db, init_teams_and_users):
        """Test same team across multiple dates"""
        from tally.models.db import User
        
        user1 = User.get(User.id == "user1")
        users = [user1]
        
        user_daily_scores = [
            UserDailyScore(user=user1, date=date(2023, 1, 15), points=10),
            UserDailyScore(user=user1, date=date(2023, 1, 16), points=15)
        ]
        
        result = get_team_daily_score(user_daily_scores, users)
        
        assert len(result) == 2
        
        # Sort results by date for consistent testing
        result.sort(key=lambda x: x.date)
        
        # Check first date
        first_score = result[0]
        assert first_score.team.id == "team1"
        assert first_score.date == date(2023, 1, 15)
        assert len(first_score.user_scores) == 1
        assert first_score.user_scores[0].points == 10
        
        # Check second date
        second_score = result[1]
        assert second_score.team.id == "team1"
        assert second_score.date == date(2023, 1, 16)
        assert len(second_score.user_scores) == 1
        assert second_score.user_scores[0].points == 15
    
    def test_complex_scenario_multiple_teams_multiple_dates(self, mock_db, init_teams_and_users):
        """Test complex scenario with multiple teams and dates"""
        from tally.models.db import User
        
        user1 = User.get(User.id == "user1")
        user2 = User.get(User.id == "user2")
        user3 = User.get(User.id == "user3")
        users = [user1, user2, user3]
        
        user_daily_scores = [
            # Team1 users on date 1
            UserDailyScore(user=user1, date=date(2023, 1, 15), points=10),
            UserDailyScore(user=user2, date=date(2023, 1, 15), points=15),
            # Team2 user on date 1
            UserDailyScore(user=user3, date=date(2023, 1, 15), points=20),
            # Team1 user on date 2
            UserDailyScore(user=user1, date=date(2023, 1, 16), points=12),
            # Team2 user on date 2
            UserDailyScore(user=user3, date=date(2023, 1, 16), points=18)
        ]
        
        result = get_team_daily_score(user_daily_scores, users)
        
        assert len(result) == 4  # 2 teams × 2 dates = 4 team daily scores
        
        # Group results by team and date for easier verification
        result_map = {(score.team.id, score.date): score for score in result}
        
        # Verify team1 on date 1
        team1_date1 = result_map[("team1", date(2023, 1, 15))]
        assert len(team1_date1.user_scores) == 2
        user_points = [score.points for score in team1_date1.user_scores]
        assert 10 in user_points and 15 in user_points
        
        # Verify team2 on date 1
        team2_date1 = result_map[("team2", date(2023, 1, 15))]
        assert len(team2_date1.user_scores) == 1
        assert team2_date1.user_scores[0].points == 20
        
        # Verify team1 on date 2
        team1_date2 = result_map[("team1", date(2023, 1, 16))]
        assert len(team1_date2.user_scores) == 1
        assert team1_date2.user_scores[0].points == 12
        
        # Verify team2 on date 2
        team2_date2 = result_map[("team2", date(2023, 1, 16))]
        assert len(team2_date2.user_scores) == 1
        assert team2_date2.user_scores[0].points == 18
    
    def test_team_user_mapping_includes_all_users(self, mock_db, init_teams_and_users):
        """Test that TeamDailyScore includes all team users, not just active ones"""
        from tally.models.db import User
        
        user1 = User.get(User.id == "user1")
        user2 = User.get(User.id == "user2")
        users = [user1, user2]
        
        # Only user1 has activity, but both users should be in team users list
        user_daily_scores = [
            UserDailyScore(user=user1, date=date(2023, 1, 15), points=10)
        ]
        
        result = get_team_daily_score(user_daily_scores, users)
        
        assert len(result) == 1
        team_score = result[0]
        assert len(team_score.users) == 2  # Both users included in team
        assert len(team_score.user_scores) == 1  # Only one user has activity
        
        # Verify both users are in the team users list
        team_user_ids = [user.id for user in team_score.users]
        assert "user1" in team_user_ids
        assert "user2" in team_user_ids
    
    def test_user_not_in_users_list_creates_team_mapping(self, mock_db, init_teams_and_users):
        """Test edge case where user in daily scores is not in users list"""
        from tally.models.db import User
        
        user1 = User.get(User.id == "user1")
        user3 = User.get(User.id == "user3")  # Different team
        
        # Pass only user1 in users list, but have user3 in daily scores
        users = [user1]
        user_daily_scores = [
            UserDailyScore(user=user3, date=date(2023, 1, 15), points=20)
        ]
        
        # This should raise a KeyError because user3's team is not in team_user_map
        with pytest.raises(KeyError):
            get_team_daily_score(user_daily_scores, users)
    
    def test_team_daily_score_aggregation_and_bonus_calculation(self, mock_db, init_teams_and_users):
        """Test that TeamDailyScore properly aggregates points and calculates bonus"""
        from tally.models.db import User
        
        user1 = User.get(User.id == "user1")
        user2 = User.get(User.id == "user2")
        users = [user1, user2]
        
        user_daily_scores = [
            UserDailyScore(user=user1, date=date(2023, 1, 15), points=10),
            UserDailyScore(user=user2, date=date(2023, 1, 15), points=15)
        ]
        
        result = get_team_daily_score(user_daily_scores, users)
        
        assert len(result) == 1
        team_score = result[0]
        
        # Test the aggregation - both users active = bonus points
        total_points = team_score.get_points()
        base_points = 10 + 15  # Sum of user points
        bonus_points = 5  # All users active = 5 bonus points
        expected_total = base_points + bonus_points
        
        assert total_points == expected_total, f"Expected {expected_total}, got {total_points}"
