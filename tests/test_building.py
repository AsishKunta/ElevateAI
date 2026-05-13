"""
Tests for the Building class.

Validates building initialization, request management, elevator coordination,
and building status tracking.
"""

import pytest
from core.building import Building
from core.request import Request


class TestBuildingInitialization:
    """Tests for building creation and initialization."""

    def test_building_created_with_correct_floor_count(self):
        """Verify building stores the correct number of floors."""
        building = Building(num_floors=10, num_elevators=2)
        assert building.num_floors == 10
        assert building.floors == 10

    def test_building_created_with_correct_elevator_count(self):
        """Verify building creates the correct number of elevators."""
        building = Building(num_floors=10, num_elevators=3)
        assert len(building.elevators) == 3

    def test_building_elevators_have_sequential_ids(self):
        """Verify elevators are created with sequential IDs starting at 0."""
        building = Building(num_floors=10, num_elevators=4)
        elevator_ids = [e.elevator_id for e in building.elevators]
        assert elevator_ids == [0, 1, 2, 3]

    def test_building_starts_with_empty_request_queues(self):
        """Verify building starts with no pending or historical requests."""
        building = Building(num_floors=10, num_elevators=2)
        assert len(building.pending_requests) == 0
        assert len(building.request_history) == 0


class TestBuildingRequestManagement:
    """Tests for adding and managing requests."""

    def test_add_request_adds_to_pending_queue(self):
        """Verify add_request() adds request to pending queue."""
        building = Building(num_floors=10, num_elevators=2)
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        building.add_request(req)
        assert req in building.pending_requests

    def test_add_request_adds_to_history(self):
        """Verify add_request() records request in history."""
        building = Building(num_floors=10, num_elevators=2)
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        building.add_request(req)
        assert req in building.request_history

    def test_multiple_requests_can_be_added(self):
        """Verify multiple requests can be added to the building."""
        building = Building(num_floors=10, num_elevators=2)
        requests = [
            Request(source_floor=2, destination_floor=8, timestamp=0),
            Request(source_floor=5, destination_floor=1, timestamp=1),
            Request(source_floor=3, destination_floor=9, timestamp=2),
        ]
        for req in requests:
            building.add_request(req)
        
        assert len(building.pending_requests) == 3
        assert len(building.request_history) == 3

    def test_get_pending_requests_only_returns_unassigned(self):
        """Verify get_pending_requests() filters out assigned requests."""
        building = Building(num_floors=10, num_elevators=2)
        req1 = Request(source_floor=2, destination_floor=8, timestamp=0)
        req2 = Request(source_floor=5, destination_floor=1, timestamp=1)
        
        building.add_request(req1)
        building.add_request(req2)
        
        # Assign req1
        req1.assign_to_elevator(0)
        
        pending = building.get_pending_requests()
        assert req1 not in pending
        assert req2 in pending
        assert len(pending) == 1


class TestBuildingElevatorManagement:
    """Tests for elevator access and management."""

    def test_get_elevators_returns_all_elevators(self):
        """Verify get_elevators() returns all building elevators."""
        building = Building(num_floors=10, num_elevators=3)
        elevators = building.get_elevators()
        assert len(elevators) == 3
        assert all(e in building.elevators for e in elevators)

    def test_get_idle_elevators_returns_only_idle(self):
        """Verify get_idle_elevators() only returns idle elevators."""
        building = Building(num_floors=10, num_elevators=2)
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        
        building.add_request(req)
        building.elevators[0].assign_request(req)
        
        idle = building.get_idle_elevators()
        assert building.elevators[0] not in idle
        assert building.elevators[1] in idle
        assert len(idle) == 1


class TestBuildingSimulationStep:
    """Tests for building step() simulation."""

    def test_step_returns_list_of_events(self):
        """Verify step() returns a list of event strings."""
        building = Building(num_floors=10, num_elevators=1)
        events = building.step(current_time=0)
        assert isinstance(events, list)

    def test_step_calls_each_elevator_step(self):
        """Verify step() calls step() on each elevator."""
        building = Building(num_floors=10, num_elevators=2)
        building.step(current_time=0)
        
        # After step, elevators should have updated their state
        for elevator in building.elevators:
            assert elevator.last_floor == 0


class TestBuildingWorkStatus:
    """Tests for checking if building has active work."""

    def test_has_work_false_when_all_idle_and_no_requests(self):
        """Verify has_work() is False when no requests and all idle."""
        building = Building(num_floors=10, num_elevators=2)
        assert not building.has_work()

    def test_has_work_true_with_pending_requests(self):
        """Verify has_work() is True when there are pending requests."""
        building = Building(num_floors=10, num_elevators=2)
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        building.add_request(req)
        assert building.has_work()

    def test_has_work_true_with_active_elevators(self):
        """Verify has_work() is True when elevators are moving."""
        building = Building(num_floors=10, num_elevators=1)
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        building.add_request(req)
        building.elevators[0].assign_request(req)
        
        assert building.has_work()


class TestBuildingStatus:
    """Tests for building status reporting."""

    def test_get_building_status_returns_dict(self):
        """Verify get_building_status() returns a dictionary."""
        building = Building(num_floors=10, num_elevators=2)
        status = building.get_building_status()
        assert isinstance(status, dict)

    def test_get_building_status_contains_required_fields(self):
        """Verify status dict contains floors, elevators, and pending_requests."""
        building = Building(num_floors=10, num_elevators=2)
        status = building.get_building_status()
        
        assert 'floors' in status
        assert 'elevators' in status
        assert 'pending_requests' in status

    def test_get_building_status_reflects_current_state(self):
        """Verify status accurately reflects building state."""
        building = Building(num_floors=10, num_elevators=2)
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        building.add_request(req)
        
        status = building.get_building_status()
        assert status['floors'] == 10
        assert status['elevators'] == 2
        assert status['pending_requests'] == 1


class TestBuildingEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_building_with_single_floor(self):
        """Verify building works with minimum floor count."""
        building = Building(num_floors=1, num_elevators=1)
        assert building.num_floors == 1
        assert len(building.elevators) == 1

    def test_building_with_single_elevator(self):
        """Verify building works with single elevator."""
        building = Building(num_floors=10, num_elevators=1)
        assert len(building.elevators) == 1

    def test_building_with_many_elevators(self):
        """Verify building can handle many elevators."""
        building = Building(num_floors=10, num_elevators=10)
        assert len(building.elevators) == 10

    def test_get_all_requests_preserves_history(self):
        """Verify get_all_requests() includes completed requests."""
        building = Building(num_floors=10, num_elevators=1)
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        building.add_request(req)
        req.completed = True
        
        all_reqs = building.get_all_requests()
        assert req in all_reqs
        assert len(all_reqs) == 1
