import pytest
import csv
import tempfile
import os
from unittest.mock import patch

from tally.actions.export.save_activity import save_activities
from tests.tally.mocks.mock_db import mock_db
from tests.tally.mocks.mock_user import create_user
from tests.tally.mocks.mock_team import create_team
from tests.tally.mocks.mock_config import create_config
from tests.tally.mocks.mock_activity import create_activity


@pytest.fixture
def init_test_data(mock_db):
    """Create test users, teams, and activities with emoji characters"""
    team = create_team(id="team1", name="Test Team")
    team.save(force_insert=True)
    user = create_user(id="user1", name="Test User", team=team.id)
    user.save(force_insert=True)
    yield user


class TestSaveActivities:
    """Test cases for save_activities function."""

    def test_empty_activities_list(self, mock_db):
        """Test with empty activities list"""
        config = create_config()

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv", newline=""
        ) as temp_file:
            temp_filename = temp_file.name

        try:
            with patch(
                "tally.actions.export.save_activity.prompt_save_file",
                return_value=temp_filename,
            ):
                save_activities([], config)

            # Verify file was created and has only header
            with open(temp_filename, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                assert len(rows) == 1  # Only header row
                assert rows[0] == [
                    "link",
                    "user_link",
                    "user",
                    "title",
                    "workout_type",
                    "date",
                    "active_time",
                ]
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_save_activity_with_emoji_characters(self, mock_db, init_test_data):
        """Test saving activity with emoji characters in title"""
        user = init_test_data
        config = create_config()

        # Create activity with emoji characters in title (similar to the reported issue)
        activity_with_emoji = create_activity(
            id="activity1",
            user=user.id,
            title="Kayaking in Killarney 🚣🌲",
            workout_type="Kayaking",
            start_time="2023-01-15T10:00:00+00:00",
            elapsed_seconds=3600,
        )
        activity_with_emoji.save(force_insert=True)

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv", newline=""
        ) as temp_file:
            temp_filename = temp_file.name

        try:
            with patch(
                "tally.actions.export.save_activity.prompt_save_file",
                return_value=temp_filename,
            ):
                # This should not raise a UnicodeEncodeError
                save_activities([activity_with_emoji], config)

            # Verify file was created and contains the emoji characters
            with open(temp_filename, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                assert len(rows) == 2  # Header + 1 data row
                assert rows[0] == [
                    "link",
                    "user_link",
                    "user",
                    "title",
                    "workout_type",
                    "date",
                    "active_time",
                ]

                # Check the activity row contains the emoji characters
                activity_row = rows[1]
                assert "🚣🌲" in activity_row[3]  # Title column should contain emojis
                assert activity_row[3] == "Kayaking in Killarney 🚣🌲"
                assert activity_row[4] == "Kayaking"
                assert (
                    activity_row[5] == "2023-01-15"
                )  # Date should be formatted correctly
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_save_multiple_activities_with_mixed_characters(
        self, mock_db, init_test_data
    ):
        """Test saving multiple activities with various Unicode characters"""
        user = init_test_data
        config = create_config()

        activities = [
            create_activity(
                id="activity1",
                user=user.id,
                title="Normal Activity",
                workout_type="Run",
                start_time="2023-01-15T10:00:00+00:00",
            ),
            create_activity(
                id="activity2",
                user=user.id,
                title="Activity with émojis and açcénts 🏃‍♂️🔥",
                workout_type="Run",
                start_time="2023-01-16T10:00:00+00:00",
            ),
            create_activity(
                id="activity3",
                user=user.id,
                title="中文 ✅",
                workout_type="Bike",
                start_time="2023-01-17T10:00:00+00:00",
            ),
        ]

        for activity in activities:
            activity.save(force_insert=True)

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv", newline=""
        ) as temp_file:
            temp_filename = temp_file.name

        try:
            with patch(
                "tally.actions.export.save_activity.prompt_save_file",
                return_value=temp_filename,
            ):
                save_activities(activities, config)

            # Verify all activities are saved correctly with Unicode characters
            with open(temp_filename, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                assert len(rows) == 4  # Header + 3 data rows

                # Check each activity title is preserved correctly
                assert rows[1][3] == "Normal Activity"
                assert rows[2][3] == "Activity with émojis and açcénts 🏃‍♂️🔥"
                assert rows[3][3] == "中文 ✅"
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_no_file_selected_skips_save(self, mock_db):
        """Test that when no file is selected, save is skipped"""
        config = create_config()

        with patch(
            "tally.actions.export.save_activity.prompt_save_file", return_value=None
        ):
            # This should not raise any exception and should print skip message
            save_activities([], config)

    def test_csv_line_endings_cross_platform(self, mock_db, init_test_data):
        """Test that CSV files have consistent line endings across platforms"""
        user = init_test_data
        config = create_config()

        activity = create_activity(
            id="activity1",
            user=user.id,
            title="Test Activity",
            workout_type="Run",
            start_time="2023-01-15T10:00:00+00:00",
        )
        activity.save(force_insert=True)

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv", newline=""
        ) as temp_file:
            temp_filename = temp_file.name

        try:
            with patch(
                "tally.actions.export.save_activity.prompt_save_file",
                return_value=temp_filename,
            ):
                save_activities([activity], config)

            # Read file in binary mode to check actual line endings
            with open(temp_filename, "rb") as f:
                content = f.read()

            # CSV standard (RFC 4180) uses \r\n line endings, which is correct
            # The newline="" parameter prevents the OS from adding extra line endings
            assert (
                b"\r\n" in content
            ), "CSV file should contain standard CSV line endings (\\r\\n)"

            # Check that we don't have double line endings (\r\r\n) which was the Windows issue
            assert (
                b"\r\r\n" not in content
            ), "CSV file should not contain doubled line endings (\\r\\r\\n)"

            # Verify content is still readable as CSV
            with open(temp_filename, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
                assert len(rows) == 2  # Header + 1 data row
                assert rows[0] == [
                    "link",
                    "user_link",
                    "user",
                    "title",
                    "workout_type",
                    "date",
                    "active_time",
                ]
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
