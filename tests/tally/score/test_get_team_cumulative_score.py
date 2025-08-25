import pytest
from datetime import date
from tally.actions.score.team_score import get_team_cumulative_score, TeamDailyScore
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

    team3 = create_team(id="team3", name="Team Gamma")
    team3.save(force_insert=True)

    # Create users for team1
    user1 = create_user(id="user1", name="Alice", team="team1")
    user1.save(force_insert=True)

    user2 = create_user(id="user2", name="Bob", team="team1")
    user2.save(force_insert=True)

    # Create users for team2
    user3 = create_user(id="user3", name="Charlie", team="team2")
    user3.save(force_insert=True)

    # Create user for team3 (team with no daily scores)
    user4 = create_user(id="user4", name="Diana", team="team3")
    user4.save(force_insert=True)

    yield


class TestGetTeamCumulativeScore:
    """Test cases for get_team_cumulative_score function."""

    def test_empty_inputs_returns_empty_list(self):
        """Test with empty team daily scores and empty users list"""
        result = get_team_cumulative_score([], [])
        assert result == []

    def test_empty_team_daily_scores_with_users(self, mock_db, init_teams_and_users):
        """Test that teams with no daily scores are included with zero points"""
        from tally.models.db import User

        users = list(User.select())
        result = get_team_cumulative_score([], users)

        # Should have 3 teams (team1, team2, team3) all with 0 points
        assert len(result) == 3

        # Sort by team id for consistent testing
        result.sort(key=lambda x: x.team.id)

        for i, team_score in enumerate(result, 1):
            assert team_score.team.id == f"team{i}"
            assert team_score.points == 0

    def test_single_team_single_daily_score(self, mock_db, init_teams_and_users):
        """Test single team with single daily score"""
        from tally.models.db import User, Team

        user1 = User.get(User.id == "user1")
        team1 = Team.get(Team.id == "team1")
        users = [user1]

        # Create a daily score with some points
        user_daily_score = UserDailyScore(user=user1, date=date(2023, 1, 15), points=10)
        team_daily_score = TeamDailyScore(
            team=team1, date=date(2023, 1, 15), users=[user1]
        )
        team_daily_score.add_user_score(user_daily_score)

        result = get_team_cumulative_score([team_daily_score], users)

        assert len(result) == 1
        assert result[0].team.id == "team1"
        assert result[0].points == team_daily_score.get_points()

    def test_single_team_multiple_daily_scores(self, mock_db, init_teams_and_users):
        """Test single team with multiple daily scores across different dates"""
        from tally.models.db import User, Team

        user1 = User.get(User.id == "user1")
        user2 = User.get(User.id == "user2")
        team1 = Team.get(Team.id == "team1")
        users = [user1, user2]

        # Create daily scores for different dates
        # Day 1: Both users active
        team_daily_score1 = TeamDailyScore(
            team=team1, date=date(2023, 1, 15), users=users
        )
        team_daily_score1.add_user_score(
            UserDailyScore(user=user1, date=date(2023, 1, 15), points=10)
        )
        team_daily_score1.add_user_score(
            UserDailyScore(user=user2, date=date(2023, 1, 15), points=15)
        )

        # Day 2: Only one user active
        team_daily_score2 = TeamDailyScore(
            team=team1, date=date(2023, 1, 16), users=users
        )
        team_daily_score2.add_user_score(
            UserDailyScore(user=user1, date=date(2023, 1, 16), points=8)
        )

        daily_scores = [team_daily_score1, team_daily_score2]
        result = get_team_cumulative_score(daily_scores, users)

        assert len(result) == 1
        assert result[0].team.id == "team1"

        # Calculate expected points: sum of both daily scores
        expected_points = (
            team_daily_score1.get_points() + team_daily_score2.get_points()
        )
        assert result[0].points == expected_points

    def test_multiple_teams_with_daily_scores(self, mock_db, init_teams_and_users):
        """Test multiple teams with various daily scores"""
        from tally.models.db import User, Team

        user1 = User.get(User.id == "user1")
        user2 = User.get(User.id == "user2")
        user3 = User.get(User.id == "user3")
        user4 = User.get(User.id == "user4")
        team1 = Team.get(Team.id == "team1")
        team2 = Team.get(Team.id == "team2")
        team3 = Team.get(Team.id == "team3")

        users = [user1, user2, user3, user4]

        # Team1: Multiple days, multiple users
        team1_day1 = TeamDailyScore(
            team=team1, date=date(2023, 1, 15), users=[user1, user2]
        )
        team1_day1.add_user_score(
            UserDailyScore(user=user1, date=date(2023, 1, 15), points=10)
        )
        team1_day1.add_user_score(
            UserDailyScore(user=user2, date=date(2023, 1, 15), points=15)
        )

        team1_day2 = TeamDailyScore(
            team=team1, date=date(2023, 1, 16), users=[user1, user2]
        )
        team1_day2.add_user_score(
            UserDailyScore(user=user1, date=date(2023, 1, 16), points=12)
        )

        # Team2: Single day, single user
        team2_day1 = TeamDailyScore(team=team2, date=date(2023, 1, 15), users=[user3])
        team2_day1.add_user_score(
            UserDailyScore(user=user3, date=date(2023, 1, 15), points=20)
        )

        # Team3: No daily scores (should still appear with 0 points)

        daily_scores = [team1_day1, team1_day2, team2_day1]
        result = get_team_cumulative_score(daily_scores, users)

        assert len(result) == 3

        # Create a map for easier verification
        result_map = {score.team.id: score for score in result}

        # Verify team1 cumulative score
        team1_score = result_map["team1"]
        expected_team1_points = team1_day1.get_points() + team1_day2.get_points()
        assert team1_score.points == expected_team1_points

        # Verify team2 cumulative score
        team2_score = result_map["team2"]
        assert team2_score.points == team2_day1.get_points()

        # Verify team3 has zero points (no daily scores)
        team3_score = result_map["team3"]
        assert team3_score.points == 0

    def test_teams_sorted_by_points_descending(self, mock_db, init_teams_and_users):
        """Test that results are sorted by points in descending order"""
        from tally.models.db import User, Team

        user1 = User.get(User.id == "user1")
        user2 = User.get(User.id == "user2")
        user3 = User.get(User.id == "user3")
        user4 = User.get(User.id == "user4")
        team1 = Team.get(Team.id == "team1")
        team2 = Team.get(Team.id == "team2")
        team3 = Team.get(Team.id == "team3")

        users = [user1, user2, user3, user4]

        # Team1: Low score (5 base points, no bonus since only 1 of 2 users active)
        team1_day1 = TeamDailyScore(
            team=team1, date=date(2023, 1, 15), users=[user1, user2]
        )
        team1_day1.add_user_score(
            UserDailyScore(user=user1, date=date(2023, 1, 15), points=5)
        )

        # Team2: High score (25 base points + 5 bonus since all users active = 30)
        team2_day1 = TeamDailyScore(team=team2, date=date(2023, 1, 15), users=[user3])
        team2_day1.add_user_score(
            UserDailyScore(user=user3, date=date(2023, 1, 15), points=25)
        )

        # Team3: Medium score (15 base points + 5 bonus since all users active = 20)
        team3_day1 = TeamDailyScore(team=team3, date=date(2023, 1, 15), users=[user4])
        team3_day1.add_user_score(
            UserDailyScore(user=user4, date=date(2023, 1, 15), points=15)
        )

        daily_scores = [team1_day1, team2_day1, team3_day1]
        result = get_team_cumulative_score(daily_scores, users)

        # Verify sorting: team2 (30) > team3 (20) > team1 (5)
        assert len(result) == 3
        assert result[0].team.id == "team2"
        assert result[0].points == 30  # 25 + 5 bonus
        assert result[1].team.id == "team3"
        assert result[1].points == 20  # 15 + 5 bonus
        assert result[2].team.id == "team1"
        assert result[2].points == 5  # 5 + 0 bonus (only 1 of 2 users active)

    def test_teams_with_equal_points_maintain_stable_sort(
        self, mock_db, init_teams_and_users
    ):
        """Test behavior when teams have equal points"""
        from tally.models.db import User, Team

        user1 = User.get(User.id == "user1")
        user2 = User.get(User.id == "user2")
        user3 = User.get(User.id == "user3")
        user4 = User.get(User.id == "user4")
        team1 = Team.get(Team.id == "team1")
        team2 = Team.get(Team.id == "team2")
        team3 = Team.get(Team.id == "team3")

        users = [user1, user2, user3, user4]

        # Team1: 10 base points, no bonus (only 1 of 2 users active) = 10 total
        team1_day1 = TeamDailyScore(
            team=team1, date=date(2023, 1, 15), users=[user1, user2]
        )
        team1_day1.add_user_score(
            UserDailyScore(user=user1, date=date(2023, 1, 15), points=10)
        )

        # Team2: 10 base points + 5 bonus (all users active) = 15 total
        team2_day1 = TeamDailyScore(team=team2, date=date(2023, 1, 15), users=[user3])
        team2_day1.add_user_score(
            UserDailyScore(user=user3, date=date(2023, 1, 15), points=10)
        )

        daily_scores = [team1_day1, team2_day1]
        result = get_team_cumulative_score(daily_scores, users)

        # Verify results: team2 (15) > team1 (10) > team3 (0)
        assert len(result) == 3  # team3 will have 0 points

        # Sort should be: team2 (15), team1 (10), team3 (0)
        assert result[0].team.id == "team2"
        assert result[0].points == 15  # 10 + 5 bonus
        assert result[1].team.id == "team1"
        assert result[1].points == 10  # 10 + 0 bonus
        assert result[2].team.id == "team3"
        assert result[2].points == 0

    def test_empty_team_daily_scores_list(self, mock_db, init_teams_and_users):
        """Test edge case with empty team daily scores but users present"""
        from tally.models.db import User

        user1 = User.get(User.id == "user1")
        user3 = User.get(User.id == "user3")
        users = [user1, user3]

        result = get_team_cumulative_score([], users)

        # Should return 2 teams (team1, team2) with 0 points each
        assert len(result) == 2

        # All teams should have 0 points
        for team_score in result:
            assert team_score.points == 0

        # Verify team IDs are correct
        team_ids = {score.team.id for score in result}
        assert team_ids == {"team1", "team2"}

    def test_duplicate_team_daily_scores_accumulate_correctly(
        self, mock_db, init_teams_and_users
    ):
        """Test that multiple daily scores for the same team accumulate correctly"""
        from tally.models.db import User, Team

        user1 = User.get(User.id == "user1")
        team1 = Team.get(Team.id == "team1")
        users = [user1]

        # Create multiple daily scores for the same team on different dates
        team_daily_score1 = TeamDailyScore(
            team=team1, date=date(2023, 1, 15), users=[user1]
        )
        team_daily_score1.add_user_score(
            UserDailyScore(user=user1, date=date(2023, 1, 15), points=10)
        )

        team_daily_score2 = TeamDailyScore(
            team=team1, date=date(2023, 1, 16), users=[user1]
        )
        team_daily_score2.add_user_score(
            UserDailyScore(user=user1, date=date(2023, 1, 16), points=15)
        )

        team_daily_score3 = TeamDailyScore(
            team=team1, date=date(2023, 1, 17), users=[user1]
        )
        team_daily_score3.add_user_score(
            UserDailyScore(user=user1, date=date(2023, 1, 17), points=8)
        )

        daily_scores = [team_daily_score1, team_daily_score2, team_daily_score3]
        result = get_team_cumulative_score(daily_scores, users)

        assert len(result) == 1
        assert result[0].team.id == "team1"

        # Points should be sum of all daily scores
        expected_points = (
            team_daily_score1.get_points()
            + team_daily_score2.get_points()
            + team_daily_score3.get_points()
        )
        assert result[0].points == expected_points

    def test_team_in_daily_scores_not_in_users_list(
        self, mock_db, init_teams_and_users
    ):
        """Test edge case where team appears in daily scores but no users from that team in users list"""
        from tally.models.db import User, Team

        user1 = User.get(User.id == "user1")
        user3 = User.get(User.id == "user3")
        team1 = Team.get(Team.id == "team1")
        team2 = Team.get(Team.id == "team2")

        # Only include user1 (team1) in users list
        users = [user1]

        # But create daily scores for both team1 and team2
        team1_day1 = TeamDailyScore(team=team1, date=date(2023, 1, 15), users=[user1])
        team1_day1.add_user_score(
            UserDailyScore(user=user1, date=date(2023, 1, 15), points=10)
        )

        team2_day1 = TeamDailyScore(team=team2, date=date(2023, 1, 15), users=[user3])
        team2_day1.add_user_score(
            UserDailyScore(user=user3, date=date(2023, 1, 15), points=20)
        )

        daily_scores = [team1_day1, team2_day1]
        result = get_team_cumulative_score(daily_scores, users)

        # Should include both teams:
        # - team1 from users list (gets initialized with 0, then updated with daily score)
        # - team2 from daily scores only (gets created when processing daily scores)
        assert len(result) == 2

        result_map = {score.team.id: score for score in result}

        # team1 should have points from daily score
        assert result_map["team1"].points == team1_day1.get_points()

        # team2 should have points from daily score
        assert result_map["team2"].points == team2_day1.get_points()
