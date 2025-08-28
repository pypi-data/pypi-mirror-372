"""Tests for the status module."""

import pytest

from pygnosis import Status


class TestStatus:
    """Tests for the Status class."""

    def test_status_of_none(self):
        """Test Status.of() with None value returns UNKNOWN."""
        assert Status.of(None) == Status.UNKNOWN

    def test_status_of_true(self):
        """Test Status.of() with True value returns UP."""
        assert Status.of(True) == Status.UP

    def test_status_of_false(self):
        """Test Status.of() with False value returns DOWN."""
        assert Status.of(False) == Status.DOWN

    def test_merge_none(self):
        """Test Status.merge() with None input returns None."""
        assert Status.merge(None) is None

    def test_merge_empty(self):
        """Test Status.merge() with empty list returns None."""
        assert Status.merge([]) is None

    @pytest.mark.parametrize(
        "status,expected",
        [
            (Status.UP, "UP"),
            (Status.DOWN, "DOWN"),
            (Status.OUT_OF_SERVICE, "OUT_OF_SERVICE"),
            (Status.UNKNOWN, "UNKNOWN"),
        ],
    )
    def test_str(self, status, expected):
        """Test string representation of status values."""
        assert str(status) == expected

    def test_merge_up(self):
        """Test Status.merge() with all UP statuses returns UP."""
        status_list = [Status.UP, Status.UP]
        assert Status.merge(status_list) == Status.UP

    def test_merge_down(self):
        """Test Status.merge() with all DOWN statuses returns DOWN."""
        status_list = [Status.DOWN, Status.DOWN]
        assert Status.merge(status_list) == Status.DOWN

    def test_merge_unknown(self):
        """Test Status.merge() with UNKNOWN status always returns UNKNOWN."""
        # UNKNOWN + UP should return UNKNOWN
        status_list = [Status.UNKNOWN, Status.UP]
        assert Status.merge(status_list) == Status.UNKNOWN

        # UNKNOWN + DOWN should return UNKNOWN
        status_list = [Status.UNKNOWN, Status.DOWN]
        assert Status.merge(status_list) == Status.UNKNOWN

        # Mixed statuses with UNKNOWN should return UNKNOWN
        status_list = [Status.OUT_OF_SERVICE, Status.UNKNOWN, Status.DOWN]
        assert Status.merge(status_list) == Status.UNKNOWN

    def test_merge_out_of_service(self):
        """Test Status.merge() with mixed statuses returns OUT_OF_SERVICE."""
        # OUT_OF_SERVICE + UP should return OUT_OF_SERVICE
        status_list = [Status.OUT_OF_SERVICE, Status.UP]
        assert Status.merge(status_list) == Status.OUT_OF_SERVICE

        # DOWN + OUT_OF_SERVICE should return OUT_OF_SERVICE
        status_list = [Status.DOWN, Status.OUT_OF_SERVICE]
        assert Status.merge(status_list) == Status.OUT_OF_SERVICE

    def test_revalidate_none_initial_status(self):
        """Test Status.revalidate() with None initial status uses summary status."""
        initial_status = None
        status_list = [Status.UP]
        assert Status.revalidate(initial_status, status_list) == Status.UP

    def test_revalidate_none_status_list(self):
        """Test Status.revalidate() with empty status list preserves initial status."""
        initial_status = Status.OUT_OF_SERVICE
        status_list = []
        assert Status.revalidate(initial_status, status_list) == Status.OUT_OF_SERVICE

    def test_revalidate_both_up(self):
        """Test Status.revalidate() with UP initial and UP components returns UP."""
        initial_status = Status.UP
        status_list = [Status.UP]
        assert Status.revalidate(initial_status, status_list) == Status.UP

    def test_revalidate_both_down(self):
        """Test Status.revalidate() with DOWN initial status preserves it regardless of components."""
        initial_status = Status.DOWN
        status_list = [Status.DOWN]
        assert Status.revalidate(initial_status, status_list) == Status.DOWN

    def test_revalidate_initial_up_list_down(self):
        """Test Status.revalidate() with UP initial status uses component status when different."""
        initial_status = Status.UP
        status_list = [Status.DOWN]
        assert Status.revalidate(initial_status, status_list) == Status.DOWN

    def test_revalidate_initial_down_list_unknown(self):
        """Test Status.revalidate() with DOWN initial status ignores component status."""
        initial_status = Status.DOWN
        status_list = [Status.OUT_OF_SERVICE]
        assert Status.revalidate(initial_status, status_list) == Status.DOWN

    def test_revalidate_both_none(self):
        """Test Status.revalidate() with both None values returns UNKNOWN."""
        initial_status = None
        status_list = None
        assert Status.revalidate(initial_status, status_list) == Status.UNKNOWN
