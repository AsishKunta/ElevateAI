"""
Base scheduler class for the ElevateAI simulator.

Abstract base class defining the interface for elevator scheduling algorithms.
All concrete schedulers should inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import List
from core.building import Building
from core.request import Request
from core.elevator import Elevator


class BaseScheduler(ABC):
    """
    Abstract base class for elevator scheduling algorithms.

    Attributes:
        building (Building): Reference to the building being managed
    """

    def __init__(self, building: Building):
        """
        Initialize the scheduler.

        Args:
            building (Building): The building to schedule for
        """
        self.building = building

    @abstractmethod
    def schedule(self, current_time: int) -> None:
        """
        Execute the scheduling algorithm.

        Args:
            current_time (int): Simulated time at the current step.

        This method should analyze pending requests and assign them
        to appropriate elevators based on the specific algorithm.
        """
        pass

    def get_pending_requests(self) -> List[Request]:
        """
        Get all pending requests from the building.

        Returns:
            List[Request]: List of pending requests
        """
        return self.building.get_pending_requests()

    def get_available_elevators(self) -> List[Elevator]:
        """
        Get elevators that are available for assignment.

        Returns:
            List[Elevator]: List of idle elevators
        """
        return [elevator for elevator in self.building.get_elevators() if elevator.is_idle()]

    def assign_request_to_elevator(self, request: Request, elevator: Elevator) -> None:
        """
        Assign a request to a target elevator.

        This method handles both request state and elevator queues.
        """
        request.assign_to_elevator(elevator.elevator_id)
        elevator.assign_request(request)
        if request in self.building.pending_requests:
            self.building.pending_requests.remove(request)

    # TODO: Add cost calculation methods
    # TODO: Add fairness metrics
    # TODO: Add congestion handling
    # TODO: Add priority handling