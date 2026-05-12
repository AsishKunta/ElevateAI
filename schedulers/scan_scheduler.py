"""
SCAN (Elevator Algorithm) scheduler for the ElevateAI simulator.

Implements the SCAN algorithm where elevators move in one direction
servicing requests along the path and only reverse direction when no
compatible requests remain in the current travel direction.
"""

from typing import List, Optional
from core.building import Building
from core.request import Request
from core.elevator import Elevator
from schedulers.base_scheduler import BaseScheduler


class SCANScheduler(BaseScheduler):
    """
    SCAN scheduler implementation.

    Maintains elevator direction persistence, batches requests along the
    current travel path, and only reverses when the current direction
    has been exhausted.
    """

    def __init__(self, building: Building):
        super().__init__(building)
        self.scan_direction = {}

    def schedule(self, current_time: int) -> None:
        """
        Run one SCAN scheduling pass at the current simulated time.

        SCAN Algorithm Logic:
        1. Elevators moving in a direction batch compatible requests ahead
        2. Idle elevators are assigned to the nearest request
        3. Remaining requests are assigned via SCAN heuristic scoring
        4. Elevators continue in their direction until no compatible requests remain
        """
        pending_requests = self.get_pending_requests()
        elevators = self.building.get_elevators()

        # Step 1: Batch requests for already-moving elevators
        # (continues their current direction efficiently)
        for elevator in elevators:
            if elevator.direction != 0:
                self._batch_requests_for_elevator(elevator, pending_requests)

        # Step 2: Assign idle elevators to nearest requests
        # (sets their initial direction)
        for elevator in elevators:
            if elevator.is_idle():
                self._assign_idle_elevator(elevator, pending_requests)

        # Step 3: Assign remaining requests using SCAN heuristics
        # (ensures optimal elevator selection)
        for request in sorted(pending_requests, key=lambda r: r.timestamp):
            best_elevator = self._select_best_elevator(request, elevators)
            if best_elevator is not None:
                self.assign_request_to_elevator(request, best_elevator)

    def _batch_requests_for_elevator(self, elevator: Elevator, pending_requests: List[Request]) -> None:
        """
        Attach compatible pending requests to a moving elevator.

        Adds same-direction requests whose source floors lie along or ahead of
        the elevator's current route.
        """
        if elevator.direction == 1:
            compatible = [
                r for r in pending_requests
                if r.direction == 1 and r.source_floor >= elevator.current_floor
            ]
            compatible.sort(key=lambda r: r.source_floor)
        elif elevator.direction == -1:
            compatible = [
                r for r in pending_requests
                if r.direction == -1 and r.source_floor <= elevator.current_floor
            ]
            compatible.sort(key=lambda r: -r.source_floor)
        else:
            return

        for request in compatible:
            self.assign_request_to_elevator(request, elevator)

    def _assign_idle_elevator(self, elevator: Elevator, pending_requests: List[Request]) -> None:
        """
        Assign the nearest SCAN-compatible request to an idle elevator.

        This sets the elevator's initial direction and begins scanning.
        """
        if not pending_requests:
            return

        same_floor = [r for r in pending_requests if r.source_floor == elevator.current_floor]
        if same_floor:
            request = same_floor[0]
            self.assign_request_to_elevator(request, elevator)
            return

        next_request = min(pending_requests, key=lambda r: abs(r.source_floor - elevator.current_floor))
        self.assign_request_to_elevator(next_request, elevator)

        if next_request.source_floor > elevator.current_floor:
            elevator.direction = 1
        elif next_request.source_floor < elevator.current_floor:
            elevator.direction = -1

    def _select_best_elevator(self, request: Request, elevators: List[Elevator]) -> Optional[Elevator]:
        """
        Select the best elevator for a request using SCAN heuristics.

        Elevator preference is:
        1. Same direction and ahead
        2. Idle elevators
        3. Opposite direction elevators
        """
        best_elevator = None
        best_score = float('inf')

        for elevator in elevators:
            score = self._score_elevator(request, elevator)
            if score < best_score:
                best_score = score
                best_elevator = elevator

        return best_elevator

    def _score_elevator(self, request: Request, elevator: Elevator) -> float:
        """
        Score an elevator for a pending request.

        Lower score is a better match.
        """
        distance = abs(elevator.current_floor - request.source_floor)
        score = distance

        if elevator.direction == 0:
            score -= 1.0
        elif elevator.direction == request.direction:
            if (request.source_floor - elevator.current_floor) * elevator.direction >= 0:
                score -= 0.5
            else:
                score += 2.0
        else:
            score += 4.0

        score += len(elevator.active_requests) * 2.0
        return score
