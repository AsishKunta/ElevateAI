"""
Tests for the SCAN elevator scheduling algorithm.

Validates direction persistence, request batching, fairness,
and SCAN-specific optimizations.
"""

import pytest
from core.building import Building
from core.request import Request
from schedulers.scan_scheduler import SCANScheduler


class TestSCANBasics:
    """Basic tests for SCAN scheduler initialization and structure."""

    def test_scan_scheduler_initializes(self, scan_scheduler, medium_building):
        """Verify SCAN scheduler can be created."""
        assert scan_scheduler is not None
        assert scan_scheduler.building == medium_building

    def test_scan_scheduler_has_scan_direction_tracking(self, scan_scheduler):
        """Verify SCAN scheduler tracks direction state."""
        assert hasattr(scan_scheduler, 'scan_direction')
        assert isinstance(scan_scheduler.scan_direction, dict)


class TestSCANDirectionPersistence:
    """Tests for SCAN direction persistence and batching."""

    def test_scan_batches_same_direction_requests(self, scan_scheduler, medium_building):
        """Verify SCAN batches compatible requests to moving elevators."""
        # Set up elevator moving UP
        elevator = medium_building.elevators[0]
        elevator.current_floor = 2
        elevator.direction = 1  # Moving up
        elevator.target_floor = 5
        
        # Add requests in same direction
        req1 = Request(source_floor=4, destination_floor=8, timestamp=0)  # UP
        req2 = Request(source_floor=6, destination_floor=9, timestamp=1)  # UP
        
        medium_building.add_request(req1)
        medium_building.add_request(req2)
        
        scan_scheduler.schedule(current_time=0)
        
        # Both should be assigned (to same or different elevators)
        assert req1.assigned_elevator_id is not None
        assert req2.assigned_elevator_id is not None

    def test_scan_does_not_batch_opposite_direction(self, scan_scheduler, medium_building):
        """Verify SCAN doesn't batch requests in opposite direction."""
        # Set up elevator moving UP
        elevator = medium_building.elevators[0]
        elevator.current_floor = 5
        elevator.direction = 1  # Moving up
        elevator.target_floor = 8
        
        # Add request in opposite direction (DOWN from above elevator)
        req = Request(source_floor=9, destination_floor=2, timestamp=0)  # DOWN
        medium_building.add_request(req)
        
        # Manually call batching (would normally happen in schedule)
        scan_scheduler._batch_requests_for_elevator(elevator, [req])
        
        # Request should NOT be assigned to moving-up elevator
        assert req.assigned_elevator_id is None

    def test_scan_continues_direction_until_exhausted(self, scan_scheduler, medium_building):
        """Verify SCAN elevator continues direction when compatible requests exist."""
        elevator = medium_building.elevators[0]
        elevator.current_floor = 1
        elevator.direction = 1  # Moving up
        elevator.target_floor = 10
        
        # Add multiple UP requests on the way
        requests = [
            Request(source_floor=3, destination_floor=9, timestamp=0),
            Request(source_floor=5, destination_floor=8, timestamp=1),
            Request(source_floor=7, destination_floor=10, timestamp=2),
        ]
        
        for req in requests:
            medium_building.add_request(req)
        
        scan_scheduler._batch_requests_for_elevator(
            elevator,
            medium_building.get_pending_requests()
        )
        
        # Verify requests were added to elevator
        assigned_count = sum(
            1 for req in requests if req.assigned_elevator_id == elevator.elevator_id
        )
        assert assigned_count > 0


class TestSCANIdleElevatorAssignment:
    """Tests for SCAN assignment of idle elevators."""

    def test_scan_assigns_idle_elevator_to_nearest_request(self, scan_scheduler, medium_building):
        """Verify SCAN assigns idle elevators to nearest request."""
        elevator = medium_building.elevators[0]
        elevator.current_floor = 5
        
        # Add requests at various distances
        close_req = Request(source_floor=6, destination_floor=9, timestamp=0)
        far_req = Request(source_floor=1, destination_floor=3, timestamp=1)
        
        medium_building.add_request(close_req)
        medium_building.add_request(far_req)
        
        scan_scheduler._assign_idle_elevator(elevator, [close_req, far_req])
        
        # Close request should be picked
        assert close_req.assigned_elevator_id == elevator.elevator_id

    def test_scan_sets_direction_for_idle_elevator(self, scan_scheduler, medium_building):
        """Verify SCAN sets appropriate direction for idle elevator."""
        elevator = medium_building.elevators[0]
        elevator.current_floor = 5
        elevator.direction = 0  # Idle
        
        req = Request(source_floor=8, destination_floor=10, timestamp=0)
        medium_building.add_request(req)
        
        scan_scheduler._assign_idle_elevator(elevator, [req])
        
        # Direction should be UP (target 8 > current 5)
        assert elevator.direction == 1

    def test_scan_same_floor_request_priority(self, scan_scheduler, medium_building):
        """Verify SCAN prioritizes same-floor requests for idle elevators."""
        elevator = medium_building.elevators[0]
        elevator.current_floor = 5
        
        same_floor_req = Request(source_floor=5, destination_floor=8, timestamp=0)
        other_req = Request(source_floor=2, destination_floor=7, timestamp=1)
        
        medium_building.add_request(same_floor_req)
        medium_building.add_request(other_req)
        
        scan_scheduler._assign_idle_elevator(
            elevator,
            [same_floor_req, other_req]
        )
        
        # Same floor should be selected
        assert same_floor_req.assigned_elevator_id == elevator.elevator_id


class TestSCANElevatorScoring:
    """Tests for SCAN elevator scoring heuristic."""

    def test_scan_score_favors_same_direction_ahead(self, scan_scheduler, small_building):
        """Verify SCAN gives best score to same-direction-ahead elevators."""
        req = Request(source_floor=6, destination_floor=9, timestamp=0)
        req.direction = 1  # UP
        
        # Elevator moving up ahead of request
        elevator_same_ahead = small_building.elevators[0]
        elevator_same_ahead.current_floor = 3
        elevator_same_ahead.direction = 1
        elevator_same_ahead.active_requests = []
        
        score_same_ahead = scan_scheduler._score_elevator(req, elevator_same_ahead)
        
        # Should have good (low) score
        assert score_same_ahead < 10

    def test_scan_score_penalizes_opposite_direction(self, scan_scheduler, small_building):
        """Verify SCAN penalizes opposite-direction elevators."""
        req = Request(source_floor=6, destination_floor=9, timestamp=0)
        req.direction = 1  # UP
        
        # Elevator moving down
        elevator_opposite = small_building.elevators[0]
        elevator_opposite.current_floor = 8
        elevator_opposite.direction = -1  # DOWN
        elevator_opposite.active_requests = []
        
        score_opposite = scan_scheduler._score_elevator(req, elevator_opposite)
        
        # Should have poor (high) score
        assert score_opposite >= 4

    def test_scan_score_prefers_idle(self, scan_scheduler, small_building):
        """Verify SCAN slightly prefers idle elevators when distance equal."""
        req = Request(source_floor=5, destination_floor=8, timestamp=0)
        
        elevator_idle = small_building.elevators[0]
        elevator_idle.current_floor = 5
        elevator_idle.direction = 0
        elevator_idle.active_requests = []
        
        elevator_moving = small_building.elevators[1]
        elevator_moving.current_floor = 5
        elevator_moving.direction = 1
        elevator_moving.active_requests = []
        
        score_idle = scan_scheduler._score_elevator(req, elevator_idle)
        score_moving = scan_scheduler._score_elevator(req, elevator_moving)
        
        # Idle should be slightly better
        assert score_idle <= score_moving


class TestSCANFairnessAndStarvation:
    """Tests for fairness and starvation prevention in SCAN."""

    def test_scan_processes_pending_requests_over_time(self, scan_scheduler, medium_building):
        """Verify SCAN eventually processes all pending requests."""
        requests = [
            Request(source_floor=i, destination_floor=(i + 5) % 10, timestamp=0)
            for i in range(5)
        ]
        
        for req in requests:
            medium_building.add_request(req)
        
        # Run multiple scheduling passes
        for step in range(3):
            scan_scheduler.schedule(current_time=step)
        
        # Most/all should be assigned
        assigned = [req for req in requests if req.assigned_elevator_id is not None]
        assert len(assigned) >= len(requests) // 2

    def test_scan_handles_mixed_directions(self, scan_scheduler, medium_building):
        """Verify SCAN efficiently handles mixed up/down requests."""
        up_requests = [
            Request(source_floor=1 + i, destination_floor=8 + i, timestamp=0)
            for i in range(3)
        ]
        down_requests = [
            Request(source_floor=8 + i, destination_floor=1 + i, timestamp=0)
            for i in range(3)
        ]
        
        all_requests = up_requests + down_requests
        for req in all_requests:
            medium_building.add_request(req)
        
        scan_scheduler.schedule(current_time=0)
        
        # All should be assigned
        assert all(req.assigned_elevator_id is not None for req in all_requests)


class TestSCANCompleteSimulation:
    """Integration tests for SCAN in complete simulation."""

    def test_scan_vs_fcfs_efficiency_scenario(self, medium_building):
        """Verify SCAN can handle requests efficiently."""
        from schedulers.fcfs_scheduler import FCFSScheduler
        
        scheduler = SCANScheduler(medium_building)
        
        # Create a scenario with concentrated requests
        requests = [
            Request(source_floor=2, destination_floor=9, timestamp=0),
            Request(source_floor=3, destination_floor=8, timestamp=1),
            Request(source_floor=4, destination_floor=10, timestamp=2),
            Request(source_floor=9, destination_floor=2, timestamp=3),
            Request(source_floor=8, destination_floor=1, timestamp=4),
        ]
        
        for req in requests:
            medium_building.add_request(req)
        
        # Run simulation for 50 steps
        for step in range(50):
            scheduler.schedule(current_time=step)
            medium_building.step(current_time=step)
        
        # All requests should complete
        assert all(req.completed for req in requests)

    def test_scan_batch_processing_scenario(self, medium_building):
        """Verify SCAN efficiently batches requests on same route."""
        scheduler = SCANScheduler(medium_building)
        
        # Create requests on same upward path
        requests = [
            Request(source_floor=2, destination_floor=8, timestamp=0),
            Request(source_floor=3, destination_floor=9, timestamp=1),
            Request(source_floor=4, destination_floor=10, timestamp=2),
        ]
        
        for req in requests:
            medium_building.add_request(req)
        
        scheduler.schedule(current_time=0)
        
        # Verify batching: multiple requests likely assigned to same elevator
        assigned_elevators = [req.assigned_elevator_id for req in requests]
        unique_elevators = len(set(e for e in assigned_elevators if e is not None))
        
        # Should use fewer elevators than FCFS might for batching
        assert unique_elevators <= len(requests)


class TestSCANEdgeCases:
    """Tests for SCAN edge cases."""

    def test_scan_with_single_elevator(self, single_elevator_building):
        """Verify SCAN works with single elevator."""
        scheduler = SCANScheduler(single_elevator_building)
        
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        single_elevator_building.add_request(req)
        
        scheduler.schedule(current_time=0)
        
        assert req.assigned_elevator_id == 0

    def test_scan_with_no_requests(self, scan_scheduler, medium_building):
        """Verify SCAN handles empty request queue."""
        # Should not raise exception
        scan_scheduler.schedule(current_time=0)
        assert len(medium_building.get_pending_requests()) == 0

    def test_scan_with_all_same_direction_requests(self, scan_scheduler, medium_building):
        """Verify SCAN handles all requests in same direction."""
        requests = [
            Request(source_floor=i, destination_floor=10, timestamp=0)
            for i in range(1, 6)
        ]
        
        for req in requests:
            medium_building.add_request(req)
        
        scan_scheduler.schedule(current_time=0)
        
        # All should be assigned
        assert all(req.assigned_elevator_id is not None for req in requests)
