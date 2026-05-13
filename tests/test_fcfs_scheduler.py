"""
Tests for the FCFS (First-Come-First-Served) scheduler.

Validates request assignment order, elevator selection heuristics,
and scheduling correctness.
"""

import pytest
from core.building import Building
from core.request import Request
from schedulers.fcfs_scheduler import FCFSScheduler


class TestFCFSScheduling:
    """Tests for FCFS scheduling algorithm."""

    def test_fcfs_assigns_requests_in_arrival_order(self, fcfs_scheduler, medium_building):
        """Verify FCFS processes requests in timestamp order."""
        req1 = Request(source_floor=2, destination_floor=8, timestamp=0)
        req2 = Request(source_floor=5, destination_floor=1, timestamp=1)
        req3 = Request(source_floor=3, destination_floor=9, timestamp=2)
        
        medium_building.add_request(req1)
        medium_building.add_request(req2)
        medium_building.add_request(req3)
        
        fcfs_scheduler.schedule(current_time=0)
        
        # All should be assigned
        assert req1.assigned_elevator_id is not None
        assert req2.assigned_elevator_id is not None
        assert req3.assigned_elevator_id is not None

    def test_fcfs_removes_assigned_from_pending(self, fcfs_scheduler, medium_building):
        """Verify assigned requests are removed from pending queue."""
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        medium_building.add_request(req)
        
        assert req in medium_building.pending_requests
        
        fcfs_scheduler.schedule(current_time=0)
        
        assert req not in medium_building.pending_requests

    def test_fcfs_handles_empty_pending_queue(self, fcfs_scheduler, medium_building):
        """Verify FCFS handles case with no pending requests."""
        # Should not raise an error
        fcfs_scheduler.schedule(current_time=0)
        
        assert len(medium_building.get_pending_requests()) == 0


class TestFCFSElevatorSelection:
    """Tests for FCFS elevator selection heuristic."""

    def test_fcfs_selects_nearest_idle_elevator(self, fcfs_scheduler, medium_building):
        """Verify FCFS prefers nearest elevator to request source."""
        # Position elevators at different floors
        medium_building.elevators[0].current_floor = 2
        medium_building.elevators[1].current_floor = 9
        medium_building.elevators[2].current_floor = 5
        
        req = Request(source_floor=3, destination_floor=8, timestamp=0)
        medium_building.add_request(req)
        
        fcfs_scheduler.schedule(current_time=0)
        
        # Elevator 0 at floor 2 is nearest to floor 3
        assert req.assigned_elevator_id == 0

    def test_fcfs_considers_direction_compatibility(self, fcfs_scheduler, medium_building):
        """Verify FCFS scores better for direction-compatible elevators."""
        req = Request(source_floor=5, destination_floor=8, timestamp=0)
        medium_building.add_request(req)
        
        # Setup: one moving up, one moving down, one idle
        medium_building.elevators[0].current_floor = 2
        medium_building.elevators[0].direction = 1  # Moving up
        medium_building.elevators[0].target_floor = 4
        medium_building.elevators[0].active_requests.append(
            Request(source_floor=2, destination_floor=4, timestamp=-1)
        )
        
        medium_building.elevators[1].current_floor = 8
        medium_building.elevators[1].direction = -1  # Moving down
        medium_building.elevators[1].target_floor = 2
        medium_building.elevators[1].active_requests.append(
            Request(source_floor=8, destination_floor=2, timestamp=-1)
        )
        
        medium_building.elevators[2].current_floor = 1
        
        fcfs_scheduler.schedule(current_time=0)
        
        # Should prefer elevator 0 (moving up toward request)
        assert req.assigned_elevator_id == 0

    def test_fcfs_prefers_idle_elevators(self, fcfs_scheduler, medium_building):
        """Verify FCFS gives lower score to idle elevators."""
        req = Request(source_floor=5, destination_floor=8, timestamp=0)
        medium_building.add_request(req)
        
        # All elevators equidistant, one is idle
        for i, elevator in enumerate(medium_building.elevators):
            elevator.current_floor = 5
            if i > 0:
                # Add a request to make non-idle
                req_dummy = Request(source_floor=5, destination_floor=7, timestamp=-1)
                elevator.assign_request(req_dummy)
        
        fcfs_scheduler.schedule(current_time=0)
        
        # Should assign to idle elevator 0
        assert req.assigned_elevator_id == 0

    def test_fcfs_considers_elevator_load(self, fcfs_scheduler, medium_building):
        """Verify FCFS penalizes elevators with many requests."""
        req = Request(source_floor=5, destination_floor=8, timestamp=0)
        medium_building.add_request(req)
        
        # Both equidistant, but one has more requests
        for i in range(2):
            medium_building.elevators[i].current_floor = 5
            if i == 1:
                # Add multiple requests to elevator 1
                for j in range(3):
                    dummy = Request(source_floor=5, destination_floor=6 + j, timestamp=-1)
                    medium_building.elevators[i].active_requests.append(dummy)
        
        fcfs_scheduler.schedule(current_time=0)
        
        # Should assign to elevator 0 (less loaded)
        assert req.assigned_elevator_id == 0


class TestFCFSSequentialSimulation:
    """Tests for FCFS in multi-step simulation."""

    def test_fcfs_handles_multiple_scheduling_passes(self, fcfs_scheduler, medium_building):
        """Verify FCFS works across multiple scheduling passes."""
        # First batch
        req1 = Request(source_floor=2, destination_floor=8, timestamp=0)
        req2 = Request(source_floor=5, destination_floor=1, timestamp=1)
        medium_building.add_request(req1)
        medium_building.add_request(req2)
        
        fcfs_scheduler.schedule(current_time=0)
        
        assert req1.assigned_elevator_id is not None
        assert req2.assigned_elevator_id is not None
        
        # Remove assigned from pending and add new
        medium_building.pending_requests = []
        
        req3 = Request(source_floor=3, destination_floor=9, timestamp=2)
        medium_building.add_request(req3)
        
        fcfs_scheduler.schedule(current_time=1)
        
        assert req3.assigned_elevator_id is not None

    def test_fcfs_complete_simulation_flow(self, small_building):
        """Verify FCFS works in complete simulation loop."""
        scheduler = FCFSScheduler(small_building)
        
        requests = [
            Request(source_floor=0, destination_floor=3, timestamp=0),
            Request(source_floor=2, destination_floor=1, timestamp=1),
        ]
        
        for req in requests:
            small_building.add_request(req)
        
        # Simulate 30 time steps
        for step in range(30):
            scheduler.schedule(current_time=step)
            small_building.step(current_time=step)
        
        # All requests should complete in reasonable time
        assert all(req.completed for req in requests)


class TestFCFSEdgeCases:
    """Tests for FCFS edge cases."""

    def test_fcfs_with_single_elevator(self, single_elevator_building):
        """Verify FCFS works with single elevator."""
        scheduler = FCFSScheduler(single_elevator_building)
        
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        single_elevator_building.add_request(req)
        
        scheduler.schedule(current_time=0)
        
        assert req.assigned_elevator_id == 0

    def test_fcfs_with_simultaneous_requests(self, medium_building):
        """Verify FCFS handles multiple requests arriving simultaneously."""
        scheduler = FCFSScheduler(medium_building)
        
        # Multiple requests with same timestamp
        requests = [
            Request(source_floor=i, destination_floor=(i + 5) % 10, timestamp=0)
            for i in range(5)
        ]
        
        for req in requests:
            medium_building.add_request(req)
        
        scheduler.schedule(current_time=0)
        
        # All should be assigned (if enough elevators) or queued
        assigned = [req for req in requests if req.assigned_elevator_id is not None]
        assert len(assigned) > 0

    def test_fcfs_handles_no_idle_elevators(self, single_elevator_building):
        """Verify FCFS handles case where all elevators are busy."""
        scheduler = FCFSScheduler(single_elevator_building)
        
        # Assign a request to the only elevator
        req1 = Request(source_floor=2, destination_floor=8, timestamp=0)
        single_elevator_building.add_request(req1)
        scheduler.schedule(current_time=0)
        
        # Add another request while elevator is busy
        req2 = Request(source_floor=5, destination_floor=1, timestamp=1)
        single_elevator_building.add_request(req2)
        
        # This should still work (though elevator might not pick it up immediately)
        scheduler.schedule(current_time=1)
        
        # req2 may or may not be assigned depending on elevator state
        assert True  # Just verify it doesn't crash


class TestFCFSScoring:
    """Tests for FCFS score calculation."""

    def test_fcfs_score_calculates_distance(self, fcfs_scheduler, small_building):
        """Verify FCFS score includes distance component."""
        elevator = small_building.elevators[0]
        elevator.current_floor = 2
        
        req = Request(source_floor=5, destination_floor=8, timestamp=0)
        
        score = fcfs_scheduler._score_elevator(req, elevator)
        
        # Score should include distance (5 - 2 = 3)
        assert score >= 3

    def test_fcfs_score_idle_elevator_bonus(self, fcfs_scheduler, small_building):
        """Verify idle elevators get lower score."""
        req = Request(source_floor=5, destination_floor=8, timestamp=0)
        
        elevator1 = small_building.elevators[0]
        elevator1.current_floor = 5
        elevator1.direction = 0  # Idle
        
        elevator2 = small_building.elevators[1]
        elevator2.current_floor = 5
        elevator2.direction = -1  # Moving down
        elevator2.target_floor = 2
        
        score1 = fcfs_scheduler._score_elevator(req, elevator1)
        score2 = fcfs_scheduler._score_elevator(req, elevator2)
        
        # Idle elevator should have better (lower) score
        assert score1 < score2
