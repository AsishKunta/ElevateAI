#!/usr/bin/env python3
"""
Simple test script for ElevateAI simulation logic.
"""

from core.building import Building
from core.request import Request
from schedulers.fcfs_scheduler import FCFSScheduler

def test_simulation():
    """Test basic simulation flow."""
    print("Testing ElevateAI Simulation...")

    # Create building
    building = Building(num_floors=10, num_elevators=2)
    scheduler = FCFSScheduler(building)

    # Create requests
    req1 = Request(2, 8, timestamp=0)
    req2 = Request(5, 1, timestamp=1)

    building.add_request(req1)
    building.add_request(req2)

    print(f"Added requests: {req1.source_floor}->{req1.destination_floor}, {req2.source_floor}->{req2.destination_floor}")

    current_time = 0
    # Simulate a few steps
    for step in range(20):
        print(f"\nStep {step}:")
        scheduler.schedule(current_time)
        events = building.step(current_time)
        for event in events:
            print(event)

        for elevator in building.elevators:
            print(f"  Elevator {elevator.elevator_id}: Floor {elevator.current_floor}, Direction {elevator.direction}, Target {elevator.target_floor}")

        current_time += 1

        for elevator in building.elevators:
            print(f"  Elevator {elevator.elevator_id}: Floor {elevator.current_floor}, Direction {elevator.direction}, Target {elevator.target_floor}")

        # Check if all requests completed
        if all(req.completed for req in [req1, req2]):
            print("All requests completed!")
            break

if __name__ == "__main__":
    test_simulation()