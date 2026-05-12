"""
Request class for the ElevateAI simulator.

Represents passenger requests for elevator service.
Handles request creation, validation, and state management.
"""


class Request:
    """
    Represents a passenger request for elevator service.

    Attributes:
        source_floor (int): Floor where request originates
        destination_floor (int): Desired destination floor
        direction (int): Direction of travel (1 for up, -1 for down)
        timestamp (int): Simulated time when request was created
        completed (bool): Whether the request has been completed
        picked_up (bool): Whether the passenger has been picked up
        assigned_elevator_id (int|None): Elevator selected to serve request
    """

    _id_counter = 0

    def __init__(self, source_floor: int, destination_floor: int, timestamp: int = 0):
        self.id = Request._id_counter
        Request._id_counter += 1

        self.source_floor = source_floor
        self.destination_floor = destination_floor
        self.direction = 1 if destination_floor > source_floor else -1
        self.timestamp = timestamp
        self.completed = False
        self.picked_up = False
        self.pickup_time = None
        self.assigned_elevator_id = None

    @property
    def origin_floor(self) -> int:
        return self.source_floor

    @property
    def priority(self) -> int:
        return 1

    def is_pending(self) -> bool:
        return not self.completed and self.assigned_elevator_id is None

    def assign_to_elevator(self, elevator_id: int) -> None:
        self.assigned_elevator_id = elevator_id
