"""Tests for CLI."""


from render_status.cli import format_timestamp, get_status_color


class TestFormatTimestamp:
    """Test timestamp formatting."""

    def test_format_valid_timestamp(self):
        """Test formatting valid ISO timestamp to local timezone."""
        result = format_timestamp("2025-11-25T12:34:56Z")
        # Just verify it contains the date/time and a timezone abbreviation
        assert "2025-11-25" in result
        assert ":" in result
        # Should have a timezone abbreviation at the end (3-4 chars)
        assert len(result.split()[-1]) >= 2

    def test_format_none_timestamp(self):
        """Test formatting None timestamp."""
        result = format_timestamp(None)
        assert result == "N/A"

    def test_format_invalid_timestamp(self):
        """Test formatting invalid timestamp."""
        result = format_timestamp("invalid")
        assert result == "invalid"


class TestGetStatusColor:
    """Test status color mapping."""

    def test_success_statuses(self):
        """Test success statuses return green."""
        assert get_status_color("live") == "green"
        assert get_status_color("succeeded") == "green"
        assert get_status_color("success") == "green"
        assert get_status_color("LIVE") == "green"

    def test_in_progress_statuses(self):
        """Test in-progress statuses return yellow."""
        assert get_status_color("building") == "yellow"
        assert get_status_color("deploying") == "yellow"
        assert get_status_color("running") == "yellow"

    def test_failure_statuses(self):
        """Test failure statuses return red."""
        assert get_status_color("build_failed") == "red"
        assert get_status_color("failed") == "red"
        assert get_status_color("canceled") == "red"

    def test_unknown_status(self):
        """Test unknown status returns white."""
        assert get_status_color("unknown") == "white"
