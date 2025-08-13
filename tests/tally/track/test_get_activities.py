from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from tally.actions.track.activity import get_activities
from tally.services.strava import StravaService
from tests.tally.mocks.mock_team import create_team
from tests.tally.mocks.mock_user import create_user
from tests.tally.mocks.mock_club_feed import (
    create_feed_response,
    create_athlete,
    create_feed_activity,
    create_feed_entry_single_activity,
)


class TestGetActivities:
    @patch("tally.actions.track.activity.time.sleep")
    def test_filter_out_activities_not_by_user_in_team(self, mock_sleep, mock_db):
        # Create a team with one user in the database
        team = create_team(id="team1", name="Test Team")
        team.save(force_insert=True)
        create_user(id="user1", name="Team Member", team=team.id).save(
            force_insert=True
        )

        # Create a mock Strava service
        mock_strava_service = MagicMock(spec=StravaService)

        # Create a mock club feed with an activity from a user NOT in the team
        user_not_in_team = create_athlete(
            athlete_id="user_not_in_team", athlete_name="Outsider"
        )
        activity_from_outsider = create_feed_activity(
            id="activity123",
            athlete=user_not_in_team,
            activity_name="Outsider's Run",
            activity_type="Run",
        )

        mock_feed = create_feed_response(
            entries=[create_feed_entry_single_activity(activity=activity_from_outsider)]
        )

        # Mock the get_club_feed method to return our mock feed
        mock_strava_service.get_club_feed.return_value = mock_feed

        # Call get_activities
        after_date = datetime.now(timezone.utc)
        result_activities = get_activities(mock_strava_service, team, after_date)

        # Assert that the activity from the user not in the team is filtered out
        assert len(result_activities) == 0

        # Verify that get_club_feed was called with the correct team id
        mock_strava_service.get_club_feed.assert_called_once_with("team1", None)

    @patch("tally.actions.track.activity.time.sleep")
    def test_include_activities_from_users_in_team(self, mock_sleep, mock_db):
        # Create a team with one user in the database
        team = create_team(id="team1", name="Test Team")
        team.save(force_insert=True)
        create_user(id="user1", name="Team Member", team=team.id).save(
            force_insert=True
        )

        # Create a mock Strava service
        mock_strava_service = MagicMock(spec=StravaService)

        # Create a mock club feed with an activity from a user IN the team
        user_in_team = create_athlete(athlete_id="user1", athlete_name="Team Member")
        activity_from_team_member = create_feed_activity(
            id="activity456",
            athlete=user_in_team,
            activity_name="Team Member's Run",
            activity_type="Run",
            elapsed_time=3600,
            start_date="2024-01-15T10:00:00Z",
        )

        mock_feed = create_feed_response(
            entries=[
                create_feed_entry_single_activity(activity=activity_from_team_member)
            ]
        )

        # Mock the get_club_feed method to return our mock feed
        mock_strava_service.get_club_feed.return_value = mock_feed

        # Call get_activities
        after_date = datetime.now(timezone.utc)
        result_activities = get_activities(mock_strava_service, team, after_date)

        # Assert that the activity from the team member is included
        assert len(result_activities) == 1

        # Verify the activity details
        activity = result_activities[0]
        assert activity.id == "activity456"
        assert activity.user.id == "user1"
        assert activity.title == "Team Member's Run"
        assert activity.workout_type == "Run"
        assert activity.elapsed_seconds == 3600

        # Verify that get_club_feed was called with the correct team id
        mock_strava_service.get_club_feed.assert_called_once_with("team1", None)
