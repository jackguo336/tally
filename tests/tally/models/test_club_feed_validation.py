import pytest
import json
from tally.models.validation.club_feed import FeedResponse
from tests.tally.mocks.mock_club_feed import get_raw_club_feed


class TestClubFeedValidation:
    """Test cases for club feed validation models."""
    
    def test_feed_response_validates_raw_club_feed(self):
        """Test that FeedResponse.model_validate works with raw club feed data"""
        # Get the raw club feed JSON string from mock
        raw_feed_json = get_raw_club_feed()
        
        # Parse the JSON string to a dictionary
        raw_feed_data = json.loads(raw_feed_json)
        
        # Validate using Pydantic model
        feed_response = FeedResponse.model_validate(raw_feed_data)
        
        # Verify the structure was parsed correctly
        assert isinstance(feed_response, FeedResponse)
        assert hasattr(feed_response, 'entries')
        assert hasattr(feed_response, 'pagination')
        
        # Verify pagination
        assert feed_response.pagination.hasMore is True
        
        # Verify entries
        assert len(feed_response.entries) == 3
        
        # Check first entry (Pilates activity)
        first_entry = feed_response.entries[0]
        assert hasattr(first_entry, 'activity')
        assert hasattr(first_entry, 'cursorData')
        assert first_entry.activity.id == "888000001"
        assert first_entry.activity.activityName == "Morning Pilates"
        assert first_entry.activity.type == "Pilates"
        assert first_entry.activity.athlete.athleteId == "777000001"
        assert first_entry.activity.athlete.athleteName == "Jane TestUser"
        assert first_entry.activity.elapsedTime == 1828
        assert first_entry.activity.startDate == "2025-09-01T14:54:19Z"
        assert first_entry.cursorData.updated_at == 1756740287
        
        # Check second entry (Bike activity)
        second_entry = feed_response.entries[1]
        assert second_entry.activity.id == "888000002"
        assert second_entry.activity.activityName == "Evening Ride"
        assert second_entry.activity.type == "Ride"
        assert second_entry.activity.athlete.athleteId == "777000002"
        assert second_entry.activity.athlete.athleteName == "Bob TestAthlete"
        assert second_entry.activity.elapsedTime == 831
        assert second_entry.activity.startDate == "2025-08-31T01:28:03Z"
        assert second_entry.cursorData.updated_at == 1756604514
        
        # Check third entry (Swim activity)
        third_entry = feed_response.entries[2]
        assert third_entry.activity.id == "888000003"
        assert third_entry.activity.activityName == "Afternoon Swim"
        assert third_entry.activity.type == "Swim"
        assert third_entry.activity.athlete.athleteId == "777000005"
        assert third_entry.activity.athlete.athleteName == "Alan TestSwimmer"
        assert third_entry.activity.elapsedTime == 1538
        assert third_entry.activity.startDate == "2025-08-30T21:05:24Z"
        assert third_entry.cursorData.updated_at == 1756589462
        
        # Verify stats are parsed correctly for first activity
        first_activity_stats = first_entry.activity.stats
        assert len(first_activity_stats) == 6
        
        # Check some specific stats
        time_stat = next((stat for stat in first_activity_stats if stat.key == "stat_one"), None)
        assert time_stat is not None
        assert "30" in time_stat.value and "28" in time_stat.value  # Time stat
        
        time_subtitle = next((stat for stat in first_activity_stats if stat.key == "stat_one_subtitle"), None)
        assert time_subtitle is not None
        assert time_subtitle.value == "Time"
        
    def test_feed_response_validation_with_invalid_data(self):
        """Test that FeedResponse validation fails with invalid data"""
        invalid_data = {
            "entries": [],
            # Missing pagination field
        }
        
        with pytest.raises(ValueError):
            FeedResponse.model_validate(invalid_data)
            
    def test_feed_response_validation_with_empty_entries(self):
        """Test that FeedResponse validates with empty entries"""
        valid_empty_data = {
            "entries": [],
            "pagination": {"hasMore": False}
        }
        
        feed_response = FeedResponse.model_validate(valid_empty_data)
        assert len(feed_response.entries) == 0
        assert feed_response.pagination.hasMore is False
