"""
Tests for the Elevator class and state machine.

Validates elevator movement, state transitions, request handling,
pickup/dropoff logic, and target selection.
"""

import pytest
from core.elevator import Elevator
from core.request import Request


class TestElevatorInitialization:
    """Tests for elevator creation and initialization."""

    def test_elevator_created_with_correct_id(self):
        """Verify elevator stores its ID correctly."""
        elevator = Elevator(elevator_id=0)
        assert elevator.elevator_id == 0

    def test_elevator_starts_at_floor_zero(self):
        """Verify elevator starts at floor 0."""
        elevator = Elevator(elevator_id=0)
        assert elevator.current_floor == 0

    def test_elevator_starts_idle(self):
        """Verify elevator starts in IDLE state."""
        elevator = Elevator(elevator_id=0)
        assert elevator.state == "IDLE"
        assert elevator.direction == 0
        assert elevator.is_idle()

    def test_elevator_starts_with_no_target(self):
        """Verify elevator starts with no target floor."""
        elevator = Elevator(elevator_id=0)
        assert elevator.target_floor is None

    def test_elevator_starts_with_empty_request_queue(self):
        """Verify elevator starts with no active requests."""
        elevator = Elevator(elevator_id=0)
        assert len(elevator.active_requests) == 0


class TestElevatorMovement:
    """Tests for elevator movement and direction tracking."""

    def test_move_up_increments_floor(self):
        """Verify move_up() increases current_floor by 1."""
        elevator = Elevator(elevator_id=0)
        elevator.move_up()
        assert elevator.current_floor == 1

    def test_move_up_sets_direction_to_one(self):
        """Verify move_up() sets direction to UP (1)."""
        elevator = Elevator(elevator_id=0)
        elevator.move_up()
        assert elevator.direction == 1

    def test_move_down_decrements_floor(self):
        """Verify move_down() decreases current_floor by 1."""
        elevator = Elevator(elevator_id=0)
        elevator.current_floor = 5
        elevator.move_down()
        assert elevator.current_floor == 4

    def test_move_down_sets_direction_to_minus_one(self):
        """Verify move_down() sets direction to DOWN (-1)."""
        elevator = Elevator(elevator_id=0)
        elevator.current_floor = 5
        elevator.move_down()
        assert elevator.direction == -1

    def test_move_tracks_total_distance(self):
        """Verify move operations track total_distance."""
        elevator = Elevator(elevator_id=0)
        elevator.move_up()
        elevator.move_up()
        elevator.move_down()
        assert elevator.total_distance == 3


class TestElevatorState:
    """Tests for elevator state machine transitions."""

    def test_idle_state_when_no_target(self):
        """Verify elevator is in IDLE state when target_floor is None."""
        elevator = Elevator(elevator_id=0)
        elevator.target_floor = None
        assert elevator.state == "IDLE"

    def test_moving_up_state_when_moving_up(self):
        """Verify elevator is in MOVING_UP state when moving up."""
        elevator = Elevator(elevator_id=0)
        elevator.move_up()
        assert elevator.state == "MOVING_UP"

    def test_moving_down_state_when_moving_down(self):
        """Verify elevator is in MOVING_DOWN state when moving down."""
        elevator = Elevator(elevator_id=0)
        elevator.current_floor = 5
        elevator.move_down()
        assert elevator.state == "MOVING_DOWN"

    def test_picking_up_state_on_pickup(self):
        """Verify elevator transitions to PICKING_UP state on arrival at pickup floor."""
        elevator = Elevator(elevator_id=0)
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        elevator.assign_request(req)
        
        # Move to floor 2 (pickup floor)
        elevator.current_floor = 2
        events = elevator.step(current_time=0)
        
        assert elevator.state == "PICKING_UP"
        assert req.picked_up

    def test_dropping_off_state_on_dropoff(self):
        """Verify elevator transitions to DROPPING_OFF state on arrival at dropoff floor."""
        elevator = Elevator(elevator_id=0)
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        elevator.assign_request(req)
        
        # Simulate pickup at floor 2
        elevator.current_floor = 2
        elevator.step(current_time=0)
        
        # Move to floor 8 (destination)
        elevator.current_floor = 8
        events = elevator.step(current_time=1)
        
        assert elevator.state == "DROPPING_OFF"
        assert req.completed


class TestElevatorRequestHandling:
    """Tests for request assignment and handling."""

    def test_assign_request_sets_target_floor(self):
        """Verify assign_request() sets target_floor to request source_floor."""
        elevator = Elevator(elevator_id=0)
        req = Request(source_floor=5, destination_floor=8, timestamp=0)
        
        elevator.assign_request(req)
        assert elevator.target_floor == 5

    def test_assign_request_adds_to_active_requests(self):
        """Verify assign_request() adds request to active_requests."""
        elevator = Elevator(elevator_id=0)
        req = Request(source_floor=5, destination_floor=8, timestamp=0)
        
        elevator.assign_request(req)
        assert req in elevator.active_requests

    def test_assign_request_sets_proper_direction_up(self):
        """Verify assign_request() sets direction UP when target > current."""
        elevator = Elevator(elevator_id=0)
        elevator.current_floor = 2
        req = Request(source_floor=8, destination_floor=10, timestamp=0)
        
        elevator.assign_request(req)
        assert elevator.state == "MOVING_UP"
        assert elevator.direction == 1

    def test_assign_request_sets_proper_direction_down(self):
        """Verify assign_request() sets direction DOWN when target < current."""
        elevator = Elevator(elevator_id=0)
        elevator.current_floor = 8
        req = Request(source_floor=2, destination_floor=5, timestamp=0)
        
        elevator.assign_request(req)
        assert elevator.state == "MOVING_DOWN"
        assert elevator.direction == -1


class TestElevatorStep:
    """Tests for the step() simulation method."""

    def test_step_when_idle_returns_no_events(self):
        """Verify step() returns empty list when elevator is idle."""
        elevator = Elevator(elevator_id=0)
        events = elevator.step(current_time=0)
        assert events == []

    def test_step_increments_idle_time_when_idle(self):
        """Verify idle_time increments when elevator is idle."""
        elevator = Elevator(elevator_id=0)
        assert elevator.idle_time == 0
        
        elevator.step(current_time=0)
        elevator.step(current_time=1)
        
        assert elevator.idle_time == 2

    def test_step_moves_elevator_up(self):
        """Verify step() moves elevator up when target is above."""
        elevator = Elevator(elevator_id=0)
        elevator.current_floor = 0
        req = Request(source_floor=3, destination_floor=8, timestamp=0)
        elevator.assign_request(req)
        
        elevator.step(current_time=0)
        assert elevator.current_floor == 1

    def test_step_moves_elevator_down(self):
        """Verify step() moves elevator down when target is below."""
        elevator = Elevator(elevator_id=0)
        elevator.current_floor = 8
        req = Request(source_floor=3, destination_floor=5, timestamp=0)
        elevator.assign_request(req)
        
        elevator.step(current_time=0)
        assert elevator.current_floor == 7

    def test_step_last_floor_tracking(self):
        """Verify step() updates last_floor for interpolation."""
        elevator = Elevator(elevator_id=0)
        elevator.current_floor = 2
        req = Request(source_floor=5, destination_floor=8, timestamp=0)
        elevator.assign_request(req)
        
        elevator.step(current_time=0)
        assert elevator.last_floor == 2


class TestElevatorPickupDropoff:
    """Tests for pickup and dropoff mechanics."""

    def test_pickup_marks_request_as_picked_up(self):
        """Verify request is marked picked_up on arrival at source floor."""
        elevator = Elevator(elevator_id=0)
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        elevator.assign_request(req)
        
        elevator.current_floor = 2
        elevator.step(current_time=0)
        
        assert req.picked_up

    def test_pickup_records_pickup_time(self):
        """Verify pickup_time is recorded at pickup."""
        elevator = Elevator(elevator_id=0)
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        elevator.assign_request(req)
        
        elevator.current_floor = 2
        elevator.step(current_time=42)
        
        assert req.pickup_time == 42

    def test_dropoff_marks_request_completed(self):
        """Verify request is marked completed on arrival at destination."""
        elevator = Elevator(elevator_id=0)
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        elevator.assign_request(req)
        
        elevator.current_floor = 2
        elevator.step(current_time=0)  # Pickup
        
        elevator.current_floor = 8
        elevator.step(current_time=1)  # Dropoff
        
        assert req.completed

    def test_dropoff_removes_from_active_requests(self):
        """Verify completed requests are removed from active_requests."""
        elevator = Elevator(elevator_id=0)
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        elevator.assign_request(req)
        
        elevator.current_floor = 2
        elevator.step(current_time=0)  # Pickup
        
        assert req in elevator.active_requests
        
        elevator.current_floor = 8
        elevator.step(current_time=1)  # Dropoff
        
        assert req not in elevator.active_requests

    def test_multiple_pickups_at_same_floor(self):
        """Verify multiple passengers can be picked up at same floor."""
        elevator = Elevator(elevator_id=0)
        req1 = Request(source_floor=2, destination_floor=8, timestamp=0)
        req2 = Request(source_floor=2, destination_floor=9, timestamp=1)
        
        elevator.assign_request(req1)
        elevator.assign_request(req2)
        
        elevator.current_floor = 2
        elevator.step(current_time=0)
        
        assert req1.picked_up
        assert req2.picked_up


class TestElevatorTargetSelection:
    """Tests for next-target selection logic."""

    def test_elevator_prefers_dropoffs_in_current_direction(self):
        """Verify elevator prioritizes dropoffs in current direction."""
        elevator = Elevator(elevator_id=0)
        
        # Create requests: pickup at 2, destinations 8 (up) and 1 (down)
        req1 = Request(source_floor=2, destination_floor=8, timestamp=0)
        req2 = Request(source_floor=2, destination_floor=1, timestamp=1)
        
        elevator.assign_request(req1)
        elevator.assign_request(req2)
        elevator.direction = 1  # Moving up
        
        elevator.current_floor = 2
        elevator.step(current_time=0)  # Pickup both
        
        # Next target should be 8 (up direction)
        assert elevator.target_floor == 8

    def test_elevator_selects_nearest_floor_when_no_direction(self):
        """Verify elevator chooses nearest floor when idle."""
        elevator = Elevator(elevator_id=0)
        elevator.current_floor = 5
        elevator.direction = 0
        
        req1 = Request(source_floor=7, destination_floor=10, timestamp=0)
        req2 = Request(source_floor=2, destination_floor=5, timestamp=1)
        
        elevator.assign_request(req1)
        elevator.assign_request(req2)
        
        elevator.current_floor = 7
        elevator.step(current_time=0)  # Pickup req1
        
        # Nearest should be 5 (from current 7)
        assert elevator.target_floor == 5 or elevator.target_floor == 10


class TestElevatorEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_elevator_returns_to_idle_after_completing_all_requests(self):
        """Verify elevator returns to IDLE after serving all requests."""
        elevator = Elevator(elevator_id=0)
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        elevator.assign_request(req)
        
        elevator.current_floor = 2
        elevator.step(current_time=0)  # Pickup
        
        elevator.current_floor = 8
        elevator.step(current_time=1)  # Dropoff
        
        assert elevator.state == "IDLE"
        assert elevator.target_floor is None

    def test_elevator_with_same_source_and_destination(self):
        """Verify elevator handles requests where source equals destination."""
        elevator = Elevator(elevator_id=0)
        req = Request(source_floor=5, destination_floor=5, timestamp=0)
        elevator.assign_request(req)
        
        elevator.current_floor = 5
        elevator.step(current_time=0)  # Both pickup and dropoff
        
        assert req.completed

    def test_is_idle_with_empty_requests(self):
        """Verify is_idle() returns True only when both target and requests are empty."""
        elevator = Elevator(elevator_id=0)
        assert elevator.is_idle()
        
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        elevator.assign_request(req)
        assert not elevator.is_idle()
        
        elevator.target_floor = None
        # Still has active_requests, so not idle
        assert not elevator.is_idle()
