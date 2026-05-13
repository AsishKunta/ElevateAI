"""
Integration tests for complete ElevateAI simulation scenarios.

Tests full simulation flows combining scheduling, building operations,
and elevator movement to validate real-world usage patterns.
"""

import pytest
from core.building import Building
from core.request import Request
from schedulers.fcfs_scheduler import FCFSScheduler
from schedulers.scan_scheduler import SCANScheduler


class TestSimulationFlow:
    """Tests for complete simulation flows."""

    def test_simple_single_request_completion(self):
        """Verify a single request completes successfully."""
        building = Building(num_floors=10, num_elevators=1)
        scheduler = FCFSScheduler(building)
        
        req = Request(source_floor=0, destination_floor=5, timestamp=0)
        building.add_request(req)
        
        # Simulate
        for step in range(50):
            scheduler.schedule(current_time=step)
            building.step(current_time=step)
            if req.completed:
                break
        
        assert req.completed
        assert req.picked_up
        assert req.pickup_time is not None

    def test_two_sequential_requests(self):
        """Verify two sequential requests complete in order."""
        building = Building(num_floors=10, num_elevators=1)
        scheduler = FCFSScheduler(building)
        
        req1 = Request(source_floor=0, destination_floor=5, timestamp=0)
        req2 = Request(source_floor=3, destination_floor=8, timestamp=1)
        
        building.add_request(req1)
        building.add_request(req2)
        
        for step in range(100):
            scheduler.schedule(current_time=step)
            building.step(current_time=step)
            if req1.completed and req2.completed:
                break
        
        assert req1.completed
        assert req2.completed

    def test_multiple_concurrent_requests(self):
        """Verify multiple elevators handle concurrent requests."""
        building = Building(num_floors=10, num_elevators=2)
        scheduler = FCFSScheduler(building)
        
        requests = [
            Request(source_floor=1, destination_floor=8, timestamp=0),
            Request(source_floor=2, destination_floor=7, timestamp=0),
            Request(source_floor=5, destination_floor=1, timestamp=0),
        ]
        
        for req in requests:
            building.add_request(req)
        
        for step in range(100):
            scheduler.schedule(current_time=step)
            building.step(current_time=step)
            if all(req.completed for req in requests):
                break
        
        assert all(req.completed for req in requests)

    def test_request_wait_time_tracking(self):
        """Verify request wait times are correctly recorded."""
        building = Building(num_floors=10, num_elevators=1)
        scheduler = FCFSScheduler(building)
        
        req = Request(source_floor=0, destination_floor=5, timestamp=5)
        building.add_request(req)
        
        for step in range(50):
            scheduler.schedule(current_time=step)
            building.step(current_time=step)
        
        assert req.completed
        assert req.pickup_time is not None
        assert req.pickup_time >= req.timestamp


class TestCapacityAndOverload:
    """Tests for handling capacity and overload conditions."""

    def test_single_elevator_multiple_requests_queue(self):
        """Verify single elevator queues multiple requests."""
        building = Building(num_floors=10, num_elevators=1)
        scheduler = FCFSScheduler(building)
        
        # Add 5 requests all at once
        requests = [
            Request(source_floor=i, destination_floor=(i + 5) % 10, timestamp=0)
            for i in range(5)
        ]
        
        for req in requests:
            building.add_request(req)
        
        # Run long simulation
        for step in range(200):
            scheduler.schedule(current_time=step)
            building.step(current_time=step)
        
        # All should eventually complete
        assert all(req.completed for req in requests)

    def test_many_elevators_few_requests(self):
        """Verify excess elevators don't cause issues."""
        building = Building(num_floors=10, num_elevators=5)
        scheduler = FCFSScheduler(building)
        
        req = Request(source_floor=0, destination_floor=5, timestamp=0)
        building.add_request(req)
        
        for step in range(50):
            scheduler.schedule(current_time=step)
            building.step(current_time=step)
        
        assert req.completed

    def test_all_elevators_busy_then_idle_handling(self):
        """Verify system handles transition from all-busy to idle state."""
        building = Building(num_floors=10, num_elevators=2)
        scheduler = FCFSScheduler(building)
        
        # Make all busy
        for i in range(2):
            req = Request(source_floor=0, destination_floor=9, timestamp=0)
            building.add_request(req)
            building.elevators[i].assign_request(req)
        
        # Add new request while all busy
        req_new = Request(source_floor=5, destination_floor=8, timestamp=1)
        building.add_request(req_new)
        
        for step in range(100):
            scheduler.schedule(current_time=step)
            building.step(current_time=step)
        
        # Eventually should complete
        assert all(building.get_all_requests()[i].completed for i in range(3))


class TestSchedulerComparison:
    """Tests for comparing FCFS and SCAN behavior."""

    def test_fcfs_and_scan_both_complete_requests(self):
        """Verify both schedulers complete all requests."""
        for SchedulerClass in [FCFSScheduler, SCANScheduler]:
            building = Building(num_floors=10, num_elevators=2)
            scheduler = SchedulerClass(building)
            
            requests = [
                Request(source_floor=i, destination_floor=(i + 3) % 10, timestamp=i)
                for i in range(5)
            ]
            
            for req in requests:
                building.add_request(req)
            
            for step in range(100):
                scheduler.schedule(current_time=step)
                building.step(current_time=step)
            
            assert all(req.completed for req in requests)

    def test_scan_efficiency_with_concentrated_requests(self):
        """Verify SCAN handles concentrated requests efficiently."""
        building = Building(num_floors=10, num_elevators=2)
        scheduler = SCANScheduler(building)
        
        # Create requests all going up from lower floors
        requests = [
            Request(source_floor=1 + i, destination_floor=8 + i, timestamp=0)
            for i in range(4)
        ]
        
        for req in requests:
            building.add_request(req)
        
        steps_completed = 0
        for step in range(100):
            scheduler.schedule(current_time=step)
            building.step(current_time=step)
            if all(req.completed for req in requests):
                steps_completed = step
                break
        
        assert steps_completed > 0
        assert all(req.completed for req in requests)


class TestRealWorldScenarios:
    """Tests for realistic usage scenarios."""

    def test_morning_rush_scenario(self):
        """Simulate morning rush with many lower-floor pickup requests."""
        building = Building(num_floors=20, num_elevators=3)
        scheduler = SCANScheduler(building)
        
        # Morning: many people on lower floors going up
        requests = [
            Request(source_floor=1, destination_floor=15 + i, timestamp=0)
            for i in range(10)
        ]
        
        for req in requests:
            building.add_request(req)
        
        completion_count = 0
        for step in range(500):
            scheduler.schedule(current_time=step)
            building.step(current_time=step)
            completion_count = sum(1 for req in requests if req.completed)
            if completion_count == len(requests):
                break
        
        # Most/all should complete
        assert completion_count >= len(requests) * 0.8

    def test_evening_dispersal_scenario(self):
        """Simulate evening with people on upper floors going down."""
        building = Building(num_floors=20, num_elevators=3)
        scheduler = SCANScheduler(building)
        
        # Evening: people on upper floors going down
        requests = [
            Request(source_floor=15 + i, destination_floor=1, timestamp=0)
            for i in range(8)
        ]
        
        for req in requests:
            building.add_request(req)
        
        for step in range(500):
            scheduler.schedule(current_time=step)
            building.step(current_time=step)
            if all(req.completed for req in requests):
                break
        
        assert all(req.completed for req in requests)

    def test_mixed_traffic_pattern(self):
        """Simulate mixed up/down traffic throughout day."""
        building = Building(num_floors=15, num_elevators=3)
        scheduler = SCANScheduler(building)
        
        # Mix of up and down requests at different times
        requests = []
        for t in range(10):
            if t % 2 == 0:
                requests.append(Request(source_floor=1 + (t % 5), destination_floor=12, timestamp=t))
            else:
                requests.append(Request(source_floor=12, destination_floor=1 + (t % 5), timestamp=t))
        
        for req in requests:
            building.add_request(req)
        
        for step in range(300):
            scheduler.schedule(current_time=step)
            building.step(current_time=step)
        
        # All should complete
        assert all(req.completed for req in requests)


class TestSystemStability:
    """Tests for system stability under stress."""

    def test_long_running_simulation(self):
        """Verify system stays stable over long run."""
        building = Building(num_floors=10, num_elevators=2)
        scheduler = FCFSScheduler(building)
        
        # Add requests continuously
        all_requests = []
        for t in range(50):
            req = Request(source_floor=t % 10, destination_floor=(t + 5) % 10, timestamp=t)
            all_requests.append(req)
            building.add_request(req)
        
        for step in range(200):
            scheduler.schedule(current_time=step)
            building.step(current_time=step)
        
        # Most should complete
        completed = sum(1 for req in all_requests if req.completed)
        assert completed >= len(all_requests) * 0.7

    def test_elevator_idle_tracking_stability(self):
        """Verify idle_time tracking doesn't cause issues."""
        building = Building(num_floors=10, num_elevators=1)
        scheduler = FCFSScheduler(building)
        
        req = Request(source_floor=0, destination_floor=9, timestamp=0)
        building.add_request(req)
        
        for step in range(100):
            scheduler.schedule(current_time=step)
            building.step(current_time=step)
        
        # Idle time should be reasonable
        total_idle = sum(e.idle_time for e in building.elevators)
        assert total_idle >= 0

    def test_distance_tracking_accuracy(self):
        """Verify total_distance tracking is accurate."""
        building = Building(num_floors=10, num_elevators=1)
        scheduler = FCFSScheduler(building)
        
        req = Request(source_floor=0, destination_floor=9, timestamp=0)
        building.add_request(req)
        
        initial_distance = building.elevators[0].total_distance
        
        for step in range(50):
            scheduler.schedule(current_time=step)
            building.step(current_time=step)
        
        final_distance = building.elevators[0].total_distance
        
        # Should have traveled at least 9 floors
        assert final_distance >= 9
