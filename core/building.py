"""
Building class for the ElevateAI simulator.

Represents the building containing elevators and manages
floor requests, elevator coordination, and system state.
"""

from typing import List
from core.elevator import Elevator
from core.request import Request


class Building:
    """
    Represents the building with multiple floors and elevators.

    Attributes:
        num_floors (int): Total number of floors
        elevators (List[Elevator]): List of elevators in the building
        pending_requests (List[Request]): Queue of unassigned requests
    """

    def __init__(self, num_floors: int, num_elevators: int):
        """
        Initialize the building.

        Args:
            num_floors (int): Number of floors in the building
            num_elevators (int): Number of elevators
        """
        self.num_floors = num_floors
        self.elevators: List[Elevator] = [Elevator(i) for i in range(num_elevators)]
        self.pending_requests: List[Request] = []
        self.request_history: List[Request] = []

    def add_request(self, request: Request) -> None:
        """
        Add a new request to the building.

        Args:
            request (Request): The request to add
        """
        self.pending_requests.append(request)
        self.request_history.append(request)

    def get_elevators(self) -> List[Elevator]:
        """
        Return the list of elevators in the building.

        Returns:
            List[Elevator]: All elevators.
        """
        return self.elevators

    def get_pending_requests(self) -> List[Request]:
        """
        Get all pending, unassigned requests.

        Returns:
            List[Request]: Pending requests.
        """
        return [request for request in self.pending_requests if not request.completed and request.assigned_elevator_id is None]

    def get_all_requests(self) -> List[Request]:
        """
        Get every request the building has received.

        Returns:
            List[Request]: All requests.
        """
        return self.request_history

    def step(self, current_time: int) -> List[str]:
        """
        Update all elevators in the building for one simulation step.

        Args:
            current_time (int): Simulated clock value.

        Returns:
            List[str]: Log events produced by elevators.
        """
        events: List[str] = []
        for elevator in self.elevators:
            events.extend(elevator.step(current_time))
        return events

    def get_idle_elevators(self) -> List[Elevator]:
        """
        Get elevators that are currently idle.

        Returns:
            List[Elevator]: List of idle elevators
        """
        return [elevator for elevator in self.elevators if elevator.is_idle()]

    def has_work(self) -> bool:
        """
        Determine whether the simulation still has active work.

        Returns:
            bool: True when there are pending requests or active elevators.
        """
        active_elevators = any(not elevator.is_idle() for elevator in self.elevators)
        pending_requests = any(self.get_pending_requests())
        return active_elevators or pending_requests

    @property
    def floors(self) -> int:
        return self.num_floors

    def get_building_status(self) -> dict:
        """
        Return a small status summary for external viewers.

        Returns:
            dict: Status with floor, elevator, and request counts.
        """
        return {
            'floors': self.num_floors,
            'elevators': len(self.elevators),
            'pending_requests': len(self.pending_requests)
        }