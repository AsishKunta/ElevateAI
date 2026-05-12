"""
Elevator class for the ElevateAI simulator.

Represents an individual elevator and its state machine.
Handles movement, pickup/dropoff, and request management.
"""

from typing import List, Optional, Literal
from core.request import Request

# Elevator state constants
ElevatorState = Literal["IDLE", "MOVING_UP", "MOVING_DOWN", "PICKING_UP", "DROPPING_OFF"]


class Elevator:
    """
    Represents an elevator in the building.

    Attributes:
        elevator_id (int): Unique identifier for the elevator
        current_floor (int): Current floor position
        direction (int): Current movement direction (-1 down, 0 idle, 1 up)
        state (ElevatorState): Current explicit state (IDLE, MOVING_UP, MOVING_DOWN, PICKING_UP, DROPPING_OFF)
        target_floor (Optional[int]): Current destination floor
        active_requests (List[Request]): Requests assigned to this elevator
        total_distance (int): Total floors traveled
        idle_time (int): Total simulated time spent idle
    """

    def __init__(self, elevator_id: int):
        self.elevator_id = elevator_id
        self.current_floor = 0
        self.last_floor = 0
        self.direction = 0
        self.state: ElevatorState = "IDLE"
        self.target_floor: Optional[int] = None
        self.active_requests: List[Request] = []
        self.total_distance = 0
        self.idle_time = 0

    def move_up(self) -> None:
        """Move the elevator up one floor and update state."""
        self.current_floor += 1
        self.total_distance += 1
        self.direction = 1
        self.state = "MOVING_UP"

    def move_down(self) -> None:
        """Move the elevator down one floor and update state."""
        self.current_floor -= 1
        self.total_distance += 1
        self.direction = -1
        self.state = "MOVING_DOWN"

    def step(self, current_time: int) -> List[str]:
        """
        Advance elevator state by one time unit.

        State transitions:
        - IDLE: no target, no active requests
        - PICKING_UP/DROPPING_OFF: at floor with passengers
        - MOVING_UP/MOVING_DOWN: traveling to target

        Args:
            current_time (int): Simulated clock value.

        Returns:
            List[str]: Event logs from this step.
        """
        events: List[str] = []
        self.last_floor = self.current_floor

        # Transition 1: No target floor → IDLE state
        if self.target_floor is None:
            self.direction = 0
            self.state = "IDLE"
            self.idle_time += 1
            return events

        # Transition 2: Moving toward target
        if self.current_floor < self.target_floor:
            self.move_up()
            events.append(f"[Time {current_time}] Elevator {self.elevator_id} moving UP to Floor {self.current_floor}")
        elif self.current_floor > self.target_floor:
            self.move_down()
            events.append(f"[Time {current_time}] Elevator {self.elevator_id} moving DOWN to Floor {self.current_floor}")
        else:
            # Transition 3: Arrival at target floor
            events.extend(self._handle_arrival(current_time))

        return events

    def _handle_arrival(self, current_time: int) -> List[str]:
        """
        Handle arrival at the current floor.

        Processes pickups and dropoffs, updating state to PICKING_UP or DROPPING_OFF
        as appropriate, then selecting the next target.
        """
        events: List[str] = []

        pickup_requests = [r for r in self.active_requests if not r.picked_up and r.source_floor == self.current_floor]
        dropoff_requests = [r for r in self.active_requests if r.picked_up and r.destination_floor == self.current_floor]

        # Transition 4: PICKING_UP state for pickups
        if pickup_requests:
            self.state = "PICKING_UP"
            for request in pickup_requests:
                request.picked_up = True
                request.pickup_time = current_time
                events.append(f"[Time {current_time}] Elevator {self.elevator_id} picked up passenger at Floor {self.current_floor} for Floor {request.destination_floor}")

        # Transition 5: DROPPING_OFF state for dropoffs
        if dropoff_requests:
            self.state = "DROPPING_OFF"
            for request in dropoff_requests:
                request.completed = True
                events.append(f"[Time {current_time}] Elevator {self.elevator_id} dropped off passenger at Floor {self.current_floor}")

        self.active_requests = [r for r in self.active_requests if not r.completed]

        # Transition 6: Select next target or go IDLE
        if self.active_requests:
            self._update_target_after_arrival()
            # If we just arrived at an intermediate stop, recurse to handle it
            if self.target_floor == self.current_floor:
                events.extend(self._handle_arrival(current_time))
        else:
            # No more active requests → IDLE
            self.target_floor = None
            self.direction = 0
            self.state = "IDLE"
            events.append(f"[Time {current_time}] Elevator {self.elevator_id} is now idle at Floor {self.current_floor}")

        return events

    def _update_target_after_arrival(self) -> None:
        """
        Select the next destination after an arrival.

        Prefers onboard dropoffs in the current travel direction,
        then pending pickups. Updates state to MOVING_UP or MOVING_DOWN.
        """
        onboard_destinations = [r.destination_floor for r in self.active_requests if r.picked_up]
        pickup_floors = [r.source_floor for r in self.active_requests if not r.picked_up]

        if onboard_destinations:
            self.target_floor = self._choose_next_stop(onboard_destinations)
        elif pickup_floors:
            self.target_floor = self._choose_next_stop(pickup_floors)
        else:
            self.target_floor = None
            self.direction = 0
            self.state = "IDLE"
            return

        # Set direction and state based on target
        if self.target_floor > self.current_floor:
            self.direction = 1
            self.state = "MOVING_UP"
        elif self.target_floor < self.current_floor:
            self.direction = -1
            self.state = "MOVING_DOWN"
        else:
            self.direction = 0

    def _choose_next_stop(self, floors: List[int]) -> int:
        """
        Choose the closest next stop from a set of floors.

        Prefers stops in the current direction when possible.

        Args:
            floors (List[int]): Candidate floors.

        Returns:
            int: Selected floor.
        """
        if self.direction == 1:
            upward = [floor for floor in floors if floor >= self.current_floor]
            if upward:
                return min(upward)
            return max(floors)
        if self.direction == -1:
            downward = [floor for floor in floors if floor <= self.current_floor]
            if downward:
                return max(downward)
            return min(floors)
        return min(floors, key=lambda floor: abs(self.current_floor - floor))

    def assign_request(self, request: Request) -> None:
        """
        Assign a request to this elevator.

        If the elevator is idle, this sets the target and updates state.

        Args:
            request (Request): The request to assign.
        """
        self.active_requests.append(request)
        if self.target_floor is None:
            self.target_floor = request.source_floor
            if self.target_floor > self.current_floor:
                self.direction = 1
                self.state = "MOVING_UP"
            elif self.target_floor < self.current_floor:
                self.direction = -1
                self.state = "MOVING_DOWN"
            else:
                self.direction = 0
                self.state = "PICKING_UP"

    def is_idle(self) -> bool:
        """Return True if the elevator is idle."""
        return self.target_floor is None and not self.active_requests
