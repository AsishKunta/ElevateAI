"""
ElevateAI - Real-Time Elevator Scheduling Simulator

Main entry point for the elevator simulation system.
Handles initialization, Pygame visualization, and the real-time loop.

Project Purpose:
A real-time elevator scheduling and optimization simulator focused on
algorithm behavior, scheduling decisions, and live visualization.
"""

import random
import sys
from core.building import Building
from core.request import Request
from schedulers.fcfs_scheduler import FCFSScheduler
from schedulers.scan_scheduler import SCANScheduler
from visualization.pygame_view import PygameView


def create_random_request(building: Building, direction: int, timestamp: int) -> Request:
    """
    Generate a random pickup request in the building.

    Args:
        building (Building): The building containing floors.
        direction (int): 1 for UP, -1 for DOWN.
        timestamp (int): Simulated time for request creation.

    Returns:
        Request: A new floor request.
    """
    if direction == 1:
        source_floor = random.randint(0, building.num_floors - 2)
        destination_floor = random.randint(source_floor + 1, building.num_floors - 1)
    else:
        source_floor = random.randint(1, building.num_floors - 1)
        destination_floor = random.randint(0, source_floor - 1)

    return Request(source_floor=source_floor, destination_floor=destination_floor, timestamp=timestamp)


def main():
    """
    Run the ElevateAI simulation with Pygame visualization.

    The simulation loop handles events, rendering, and engine updates
    while keeping the visualization layer separate from the scheduling logic.
    """
    print("ElevateAI Elevator Simulation Starting...")

    building = Building(num_floors=10, num_elevators=2)
    current_algorithm = "SCAN"
    scheduler = SCANScheduler(building)
    view = PygameView(building, width=1200, height=760, fps=30)
    view.current_algorithm = current_algorithm

    current_time = 0
    step_interval = 1.0
    time_since_step = 0.0
    paused = False

    sample_requests = [
        Request(source_floor=2, destination_floor=8, timestamp=current_time),
        Request(source_floor=5, destination_floor=1, timestamp=current_time + 1),
        Request(source_floor=0, destination_floor=9, timestamp=current_time + 2),
        Request(source_floor=7, destination_floor=3, timestamp=current_time + 3),
    ]

    for request in sample_requests:
        building.add_request(request)
        print(f"[Time {current_time}] Request added: Floor {request.source_floor} -> Floor {request.destination_floor}")
        current_time += 1

    current_time = 0

    try:
        running = True
        while running:
            dt = view.clock.tick(view.fps) / 1000.0
            controls = view.handle_events()

            if controls["quit"]:
                running = False
            if controls["toggle_pause"]:
                paused = not paused
            if controls["new_up_request"]:
                request = create_random_request(building, direction=1, timestamp=current_time)
                building.add_request(request)
                print(f"[Time {current_time}] UP request generated at Floor {request.source_floor} -> {request.destination_floor}")
            if controls["new_down_request"]:
                request = create_random_request(building, direction=-1, timestamp=current_time)
                building.add_request(request)
                print(f"[Time {current_time}] DOWN request generated at Floor {request.source_floor} -> {request.destination_floor}")

            if controls["toggle_algorithm"]:
                if current_algorithm == "SCAN":
                    current_algorithm = "FCFS"
                    scheduler = FCFSScheduler(building)
                else:
                    current_algorithm = "SCAN"
                    scheduler = SCANScheduler(building)
                view.current_algorithm = current_algorithm
                print(f"Switched scheduling algorithm to {current_algorithm}")

            if not paused:
                time_since_step += dt
                view.set_step_progress(time_since_step / step_interval)

            if not paused and time_since_step >= step_interval:
                scheduler.schedule(current_time)
                events = building.step(current_time)
                for event in events:
                    print(event)
                current_time += 1
                time_since_step -= step_interval
                view.set_step_progress(0.0)

            view.paused = paused
            view.render(current_time)

        print("Simulation terminated.")

    except KeyboardInterrupt:
        print("Simulation stopped by user.")
    finally:
        view.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
