"""
FCFS (First-Come, First-Served) scheduler for the ElevateAI simulator.

Implements a simple scheduling algorithm where requests are served
in the order they arrive, assigned to the nearest available elevator.
"""

from typing import List
from core.building import Building
from core.request import Request
from core.elevator import Elevator
from schedulers.base_scheduler import BaseScheduler


class FCFSScheduler(BaseScheduler):
    """
    First-Come, First-Served elevator scheduling algorithm.

    Requests are processed in chronological order and assigned
    to the nearest available elevator.
    """

    def __init__(self, building: Building):
        """
        Initialize the FCFS scheduler.

        Args:
            building (Building): The building to schedule for
        """
        super().__init__(building)

    def schedule(self, current_time: int) -> None:
        """
        Execute FCFS scheduling algorithm.

        Args:
            current_time (int): Current simulated time.

        FCFS Flow:
        1. Process pending requests in order of arrival (timestamp)
        2. For each pending request, find nearest idle elevator
        3. Assign request to that elevator
        4. Elevator moves to source floor, picks up passenger
        5. Elevator moves to destination floor, drops off passenger
        6. Mark request as completed
        """
        pending_requests = sorted(
            [r for r in self.get_pending_requests() if r.timestamp <= current_time],
            key=lambda r: r.timestamp
        )
        elevators = self.building.get_elevators()

        # Assign pending requests to the best available elevator
        for request in pending_requests:
            if not elevators:
                break

            best_elevator = min(
                elevators,
                key=lambda elevator: self._score_elevator(request, elevator)
            )
            self.assign_request_to_elevator(request, best_elevator)

    def _score_elevator(self, request: Request, elevator: Elevator) -> float:
        """
        Compute a heuristic score for assigning a request to an elevator.

        A lower score indicates a better match based on distance, direction,
        current load, and idle status.
        """
        score = abs(elevator.current_floor - request.source_floor)

        if elevator.direction == 0:
            pass  # Idle elevators don't get special bonus; distance is primary factor
        elif elevator.direction == request.direction:
            if (request.source_floor - elevator.current_floor) * elevator.direction >= 0:
                score -= 0.5
            else:
                score += 2.0
        else:
            score += 5.0

        score += len(elevator.active_requests) * 1.0

        if elevator.target_floor is not None and elevator.target_floor == request.source_floor:
            score -= 0.5

        return score
