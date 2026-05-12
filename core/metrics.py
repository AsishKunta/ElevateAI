"""
Metrics class for the ElevateAI simulator.

Handles collection, calculation, and reporting of system performance metrics.
Tracks elevator efficiency, passenger satisfaction, and system utilization.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from core.request import Request
from core.elevator import Elevator


class Metrics:
    """
    Collects and analyzes performance metrics for the elevator system.

    Attributes:
        total_requests (int): Total number of requests processed
        served_requests (int): Number of successfully served requests
        average_wait_time (float): Average wait time in seconds
        average_travel_time (float): Average travel time in seconds
        elevator_utilization (Dict[int, float]): Utilization per elevator
        system_uptime (timedelta): Total system uptime
    """

    def __init__(self):
        """Initialize metrics tracking."""
        self.start_time = datetime.now()
        self.total_requests = 0
        self.served_requests = 0
        self.wait_times: List[float] = []
        self.travel_times: List[float] = []
        self.elevator_utilization: Dict[int, float] = {}
        self.request_history: List[Dict[str, Any]] = []

        # TODO: Add peak hour analysis
        # TODO: Add congestion metrics
        # TODO: Add energy consumption tracking
        # TODO: Add passenger satisfaction scoring
        # TODO: Add real-time metrics streaming

    def record_request(self, request: Request) -> None:
        """
        Record a new request.

        Args:
            request (Request): The request being recorded
        """
        self.total_requests += 1
        self.request_history.append({
            'id': request.id,
            'origin': request.origin_floor,
            'destination': request.destination_floor,
            'timestamp': request.timestamp,
            'priority': request.priority
        })

    def record_served_request(self, request: Request, wait_time: float, travel_time: float) -> None:
        """
        Record a served request with timing information.

        Args:
            request (Request): The served request
            wait_time (float): Time spent waiting
            travel_time (float): Time spent traveling
        """
        self.served_requests += 1
        self.wait_times.append(wait_time)
        self.travel_times.append(travel_time)

        # Update request history
        for req in self.request_history:
            if req['id'] == request.id:
                req['served_time'] = datetime.now()
                req['wait_time'] = wait_time
                req['travel_time'] = travel_time
                break

    def update_elevator_utilization(self, elevators: List[Elevator]) -> None:
        """
        Update utilization metrics for all elevators.

        Args:
            elevators (List[Elevator]): List of elevators to analyze
        """
        # TODO: Implement utilization calculation
        # This would track time spent idle vs active
        pass

    def get_average_wait_time(self) -> float:
        """
        Calculate average wait time.

        Returns:
            float: Average wait time in seconds
        """
        if not self.wait_times:
            return 0.0
        return sum(self.wait_times) / len(self.wait_times)

    def get_average_travel_time(self) -> float:
        """
        Calculate average travel time.

        Returns:
            float: Average travel time in seconds
        """
        if not self.travel_times:
            return 0.0
        return sum(self.travel_times) / len(self.travel_times)

    def get_system_efficiency(self) -> float:
        """
        Calculate overall system efficiency.

        Returns:
            float: Efficiency score (0.0 to 1.0)
        """
        if self.total_requests == 0:
            return 0.0
        return self.served_requests / self.total_requests

    def get_summary_report(self) -> Dict[str, Any]:
        """
        Generate a summary report of all metrics.

        Returns:
            Dict[str, Any]: Summary metrics
        """
        uptime = datetime.now() - self.start_time

        return {
            'total_requests': self.total_requests,
            'served_requests': self.served_requests,
            'efficiency': self.get_system_efficiency(),
            'average_wait_time': self.get_average_wait_time(),
            'average_travel_time': self.get_average_travel_time(),
            'system_uptime_seconds': uptime.total_seconds(),
            'elevator_utilization': self.elevator_utilization
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.__init__()