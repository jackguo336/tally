from tally.actions.track.activity import get_moving_seconds_from_stats
from tally.models.validation.club_feed import ActivityStatsEntry


class TestGetMovingSecondsFromStats:
    """Test cases for get_moving_seconds_from_stats function."""

    def test_empty_stats_list_returns_none(self):
        """Test with empty stats list"""
        result = get_moving_seconds_from_stats([])
        assert result is None

    def test_no_matching_entries_returns_none(self):
        """Test with stats that don't contain moving time entries"""
        stats = [
            ActivityStatsEntry(key="distance", value="5.2 km"),
            ActivityStatsEntry(key="elevation", value="100 m"),
            ActivityStatsEntry(key="pace", value="4:30 /km"),
        ]
        result = get_moving_seconds_from_stats(stats)
        assert result is None

    def test_minutes_and_seconds_format(self):
        """Test parsing minutes and seconds format"""
        stats = [
            ActivityStatsEntry(
                key="moving_time",
                value="22<abbr class='unit' title='minute'>m</abbr> 30<abbr class='unit' title='second'>s</abbr>",
            )
        ]
        result = get_moving_seconds_from_stats(stats)
        expected = 22 * 60 + 30  # 22 minutes + 30 seconds = 1350 seconds
        assert result == expected

    def test_hours_and_minutes_format(self):
        """Test parsing hours and minutes format"""
        stats = [
            ActivityStatsEntry(
                key="moving_time",
                value="1<abbr class='unit' title='hour'>h</abbr> 22<abbr class='unit' title='minute'>m</abbr>",
            )
        ]
        result = get_moving_seconds_from_stats(stats)
        expected = 1 * 3600 + 22 * 60  # 1 hour + 22 minutes = 4920 seconds
        assert result == expected

    def test_hours_and_minutes_multiple_hours(self):
        """Test parsing hours and minutes with multiple hours"""
        stats = [
            ActivityStatsEntry(
                key="moving_time",
                value="2<abbr class='unit' title='hour'>h</abbr> 45<abbr class='unit' title='minute'>m</abbr>",
            )
        ]
        result = get_moving_seconds_from_stats(stats)
        expected = 2 * 3600 + 45 * 60  # 2 hours + 45 minutes = 9900 seconds
        assert result == expected

    def test_zero_minutes_with_seconds(self):
        """Test parsing with zero minutes and some seconds"""
        stats = [
            ActivityStatsEntry(
                key="moving_time",
                value="0<abbr class='unit' title='minute'>m</abbr> 45<abbr class='unit' title='second'>s</abbr>",
            )
        ]
        result = get_moving_seconds_from_stats(stats)
        expected = 0 * 60 + 45  # 45 seconds
        assert result == expected

    def test_zero_seconds_with_minutes(self):
        """Test parsing with some minutes and zero seconds"""
        stats = [
            ActivityStatsEntry(
                key="moving_time",
                value="15<abbr class='unit' title='minute'>m</abbr> 0<abbr class='unit' title='second'>s</abbr>",
            )
        ]
        result = get_moving_seconds_from_stats(stats)
        expected = 15 * 60 + 0  # 15 minutes = 900 seconds
        assert result == expected

    def test_zero_hours_with_minutes(self):
        """Test parsing with zero hours and some minutes"""
        stats = [
            ActivityStatsEntry(
                key="moving_time",
                value="0<abbr class='unit' title='hour'>h</abbr> 30<abbr class='unit' title='minute'>m</abbr>",
            )
        ]
        result = get_moving_seconds_from_stats(stats)
        expected = 0 * 3600 + 30 * 60  # 30 minutes = 1800 seconds
        assert result == expected

    def test_zero_minutes_with_hours(self):
        """Test parsing with some hours and zero minutes"""
        stats = [
            ActivityStatsEntry(
                key="moving_time",
                value="1<abbr class='unit' title='hour'>h</abbr> 0<abbr class='unit' title='minute'>m</abbr>",
            )
        ]
        result = get_moving_seconds_from_stats(stats)
        expected = 1 * 3600 + 0 * 60  # 1 hour = 3600 seconds
        assert result == expected

    def test_multiple_stats_entries_returns_first_match(self):
        """Test that with multiple stats entries, the first matching one is used"""
        stats = [
            ActivityStatsEntry(key="distance", value="5.2 km"),
            ActivityStatsEntry(
                key="moving_time",
                value="10<abbr class='unit' title='minute'>m</abbr> 30<abbr class='unit' title='second'>s</abbr>",
            ),
            ActivityStatsEntry(
                key="another_time",
                value="20<abbr class='unit' title='minute'>m</abbr> 45<abbr class='unit' title='second'>s</abbr>",
            ),
        ]
        result = get_moving_seconds_from_stats(stats)
        expected = (
            10 * 60 + 30
        )  # First matching entry: 10 minutes + 30 seconds = 630 seconds
        assert result == expected

    def test_hours_format_takes_precedence_over_minutes(self):
        """Test that hours format is matched first when both patterns exist"""
        stats = [
            ActivityStatsEntry(
                key="time1",
                value="1<abbr class='unit' title='hour'>h</abbr> 30<abbr class='unit' title='minute'>m</abbr>",
            ),
            ActivityStatsEntry(
                key="time2",
                value="45<abbr class='unit' title='minute'>m</abbr> 20<abbr class='unit' title='second'>s</abbr>",
            ),
        ]
        result = get_moving_seconds_from_stats(stats)
        expected = (
            1 * 3600 + 30 * 60
        )  # Hours format: 1 hour + 30 minutes = 5400 seconds
        assert result == expected

    def test_whitespace_variations_in_format(self):
        """Test parsing with various whitespace patterns"""
        test_cases = [
            (
                "22<abbr class='unit' title='minute'>m</abbr>30<abbr class='unit' title='second'>s</abbr>",
                22 * 60 + 30,
            ),
            (
                "22 <abbr class='unit' title='minute'>m</abbr> 30 <abbr class='unit' title='second'>s</abbr>",
                22 * 60 + 30,
            ),
            (
                "1<abbr class='unit' title='hour'>h</abbr>22<abbr class='unit' title='minute'>m</abbr>",
                1 * 3600 + 22 * 60,
            ),
            (
                "1 <abbr class='unit' title='hour'>h</abbr> 22 <abbr class='unit' title='minute'>m</abbr>",
                1 * 3600 + 22 * 60,
            ),
        ]

        for time_value, expected in test_cases:
            stats = [ActivityStatsEntry(key="moving_time", value=time_value)]
            result = get_moving_seconds_from_stats(stats)
            assert result == expected, f"Failed for time_value: {time_value}"

    def test_different_abbr_attributes(self):
        """Test parsing with different abbr tag attributes"""
        test_cases = [
            # Different class names
            (
                "22<abbr title='minute'>m</abbr> 30<abbr title='second'>s</abbr>",
                22 * 60 + 30,
            ),
            # Different attribute order
            (
                "1<abbr title='hour' class='unit'>h</abbr> 22<abbr title='minute' class='unit'>m</abbr>",
                1 * 3600 + 22 * 60,
            ),
            # Additional attributes
            (
                "22<abbr class='unit time' title='minute' data-test='true'>m</abbr> 30<abbr class='unit time' title='second' data-test='true'>s</abbr>",
                22 * 60 + 30,
            ),
        ]

        for time_value, expected in test_cases:
            stats = [ActivityStatsEntry(key="moving_time", value=time_value)]
            result = get_moving_seconds_from_stats(stats)
            assert result == expected, f"Failed for time_value: {time_value}"

    def test_large_numbers(self):
        """Test parsing with large hour values"""
        stats = [
            ActivityStatsEntry(
                key="moving_time",
                value="12<abbr class='unit' title='hour'>h</abbr> 45<abbr class='unit' title='minute'>m</abbr>",
            )
        ]
        result = get_moving_seconds_from_stats(stats)
        expected = 12 * 3600 + 45 * 60  # 12 hours + 45 minutes = 45900 seconds
        assert result == expected

    def test_single_digit_and_double_digit_numbers(self):
        """Test parsing with both single and double digit numbers"""
        test_cases = [
            (
                "5<abbr class='unit' title='minute'>m</abbr> 3<abbr class='unit' title='second'>s</abbr>",
                5 * 60 + 3,
            ),
            (
                "59<abbr class='unit' title='minute'>m</abbr> 59<abbr class='unit' title='second'>s</abbr>",
                59 * 60 + 59,
            ),
            (
                "3<abbr class='unit' title='hour'>h</abbr> 7<abbr class='unit' title='minute'>m</abbr>",
                3 * 3600 + 7 * 60,
            ),
        ]

        for time_value, expected in test_cases:
            stats = [ActivityStatsEntry(key="moving_time", value=time_value)]
            result = get_moving_seconds_from_stats(stats)
            assert result == expected, f"Failed for time_value: {time_value}"

    def test_malformed_html_does_not_match(self):
        """Test that malformed HTML does not match the regex patterns"""
        malformed_cases = [
            "22m 30s",  # No abbr tags
            "22<abbr>m</abbr> 30<abbr>s</abbr>",  # No title attribute
            "22<abbr title='minutes'>m</abbr> 30<abbr title='seconds'>s</abbr>",  # Wrong title values
            "1h 22m",  # No abbr tags
            "1<abbr title='hours'>h</abbr> 22<abbr title='minutes'>m</abbr>",  # Wrong title values
            "<abbr title='minute'>22m</abbr> <abbr title='second'>30s</abbr>",  # Numbers inside tags
        ]

        for time_value in malformed_cases:
            stats = [ActivityStatsEntry(key="moving_time", value=time_value)]
            result = get_moving_seconds_from_stats(stats)
            assert result is None, f"Should not match malformed HTML: {time_value}"

    def test_partial_formats_now_match(self):
        """Test that partial time formats now match (updated behavior)"""
        partial_cases = [
            ("22<abbr class='unit' title='minute'>m</abbr>", 22 * 60),  # Only minutes
            ("30<abbr class='unit' title='second'>s</abbr>", 30),  # Only seconds
            ("1<abbr class='unit' title='hour'>h</abbr>", 1 * 3600),  # Only hours
        ]

        for time_value, expected in partial_cases:
            stats = [ActivityStatsEntry(key="moving_time", value=time_value)]
            result = get_moving_seconds_from_stats(stats)
            assert (
                result == expected
            ), f"Should match partial format: {time_value}, expected: {expected}, got: {result}"

    def test_all_three_units_combined(self):
        """Test parsing time with hours, minutes, and seconds all present"""
        stats = [
            ActivityStatsEntry(
                key="moving_time",
                value="2<abbr class='unit' title='hour'>h</abbr> 30<abbr class='unit' title='minute'>m</abbr> 45<abbr class='unit' title='second'>s</abbr>",
            )
        ]
        result = get_moving_seconds_from_stats(stats)
        expected = (
            2 * 3600 + 30 * 60 + 45
        )  # 2 hours + 30 minutes + 45 seconds = 9045 seconds
        assert result == expected

    def test_hours_and_seconds_without_minutes(self):
        """Test parsing time with hours and seconds but no minutes"""
        stats = [
            ActivityStatsEntry(
                key="moving_time",
                value="1<abbr class='unit' title='hour'>h</abbr> 30<abbr class='unit' title='second'>s</abbr>",
            )
        ]
        result = get_moving_seconds_from_stats(stats)
        expected = 1 * 3600 + 30  # 1 hour + 30 seconds = 3630 seconds
        assert result == expected
