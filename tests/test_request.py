"""
Tests for the Request class.

Validates request creation, state management, direction inference,
and assignment tracking.
"""

import pytest
from core.request import Request


class TestRequestCreation:
    """Tests for request creation and initialization."""

    def test_request_created_with_correct_floors(self):
        """Verify request stores source and destination floors correctly."""
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        assert req.source_floor == 2
        assert req.destination_floor == 8

    def test_request_direction_inference_up(self):
        """Verify direction is set to UP (1) when destination > source."""
        req = Request(source_floor=3, destination_floor=7, timestamp=0)
        assert req.direction == 1

    def test_request_direction_inference_down(self):
        """Verify direction is set to DOWN (-1) when destination < source."""
        req = Request(source_floor=8, destination_floor=2, timestamp=0)
        assert req.direction == -1

    def test_request_timestamp_stored(self):
        """Verify request timestamp is stored and retrievable."""
        req = Request(source_floor=2, destination_floor=8, timestamp=42)
        assert req.timestamp == 42

    def test_request_default_timestamp_is_zero(self):
        """Verify default timestamp is 0 when not provided."""
        req = Request(source_floor=2, destination_floor=8)
        assert req.timestamp == 0


class TestRequestState:
    """Tests for request state management and transitions."""

    def test_request_initial_state_is_pending(self):
        """Verify new request starts as pending (not completed, not picked up)."""
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        assert not req.completed
        assert not req.picked_up
        assert req.assigned_elevator_id is None

    def test_request_is_pending_returns_true_when_unassigned(self):
        """Verify is_pending() returns True for unassigned requests."""
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        assert req.is_pending()

    def test_request_is_pending_returns_false_when_assigned(self):
        """Verify is_pending() returns False after elevator assignment."""
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        req.assign_to_elevator(0)
        assert not req.is_pending()

    def test_request_assign_to_elevator_stores_id(self):
        """Verify assign_to_elevator() stores the elevator ID."""
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        req.assign_to_elevator(1)
        assert req.assigned_elevator_id == 1

    def test_request_can_track_pickup_time(self):
        """Verify pickup_time can be recorded."""
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        req.pickup_time = 5
        assert req.pickup_time == 5


class TestRequestProperties:
    """Tests for request property accessors."""

    def test_origin_floor_alias_for_source_floor(self):
        """Verify origin_floor property returns source_floor."""
        req = Request(source_floor=3, destination_floor=7, timestamp=0)
        assert req.origin_floor == 3
        assert req.origin_floor == req.source_floor

    def test_priority_default_value(self):
        """Verify default priority is 1."""
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        assert req.priority == 1


class TestRequestIDGeneration:
    """Tests for unique request ID generation."""

    def test_request_ids_are_unique(self):
        """Verify each request gets a unique ID."""
        requests = [Request(source_floor=2, destination_floor=8, timestamp=i) for i in range(5)]
        ids = [req.id for req in requests]
        assert len(ids) == len(set(ids)), "Request IDs should be unique"

    def test_request_ids_increment(self):
        """Verify request IDs increment sequentially."""
        req1 = Request(source_floor=2, destination_floor=8, timestamp=0)
        req2 = Request(source_floor=3, destination_floor=9, timestamp=1)
        req3 = Request(source_floor=4, destination_floor=10, timestamp=2)
        assert req2.id == req1.id + 1
        assert req3.id == req2.id + 1


class TestRequestValidation:
    """Tests for request validation and edge cases."""

    def test_request_with_same_source_and_destination(self):
        """Verify request can be created even with identical floors (edge case)."""
        req = Request(source_floor=5, destination_floor=5, timestamp=0)
        assert req.source_floor == 5
        assert req.destination_floor == 5
        # Direction would be -1 (down) for same floor
        assert req.direction == -1

    def test_request_with_timestamp_zero(self):
        """Verify request can be created with timestamp 0."""
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        assert req.timestamp == 0

    def test_request_with_large_floor_numbers(self):
        """Verify request works with large floor numbers."""
        req = Request(source_floor=50, destination_floor=100, timestamp=0)
        assert req.source_floor == 50
        assert req.destination_floor == 100
        assert req.direction == 1

    def test_request_with_negative_floor_numbers(self):
        """Verify request can handle basement floors (negative numbers)."""
        req = Request(source_floor=-1, destination_floor=5, timestamp=0)
        assert req.source_floor == -1
        assert req.direction == 1
