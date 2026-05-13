"""
Shared pytest fixtures for ElevateAI tests.

Provides reusable building, elevator, and scheduler instances
for consistent test setup across the test suite.
"""

import pytest
from core.building import Building
from core.request import Request
from core.elevator import Elevator
from schedulers.fcfs_scheduler import FCFSScheduler
from schedulers.scan_scheduler import SCANScheduler


@pytest.fixture
def small_building():
    """Create a small test building with 5 floors and 2 elevators."""
    return Building(num_floors=5, num_elevators=2)


@pytest.fixture
def medium_building():
    """Create a medium test building with 10 floors and 3 elevators."""
    return Building(num_floors=10, num_elevators=3)


@pytest.fixture
def tall_building():
    """Create a tall test building with 20 floors and 4 elevators."""
    return Building(num_floors=20, num_elevators=4)


@pytest.fixture
def single_elevator_building():
    """Create a building with only 1 elevator for bottleneck testing."""
    return Building(num_floors=10, num_elevators=1)


@pytest.fixture
def fcfs_scheduler(medium_building):
    """Create an FCFS scheduler instance for the medium building."""
    return FCFSScheduler(medium_building)


@pytest.fixture
def scan_scheduler(medium_building):
    """Create a SCAN scheduler instance for the medium building."""
    return SCANScheduler(medium_building)


@pytest.fixture
def simple_request():
    """Create a simple UP request from floor 2 to floor 8."""
    return Request(source_floor=2, destination_floor=8, timestamp=0)


@pytest.fixture
def mixed_requests():
    """
    Create a set of mixed direction requests for realistic scenarios.
    
    Returns:
        Tuple of 4 requests: (up1, down1, up2, down2)
    """
    req_up_1 = Request(source_floor=2, destination_floor=8, timestamp=0)
    req_down_1 = Request(source_floor=7, destination_floor=1, timestamp=1)
    req_up_2 = Request(source_floor=3, destination_floor=9, timestamp=2)
    req_down_2 = Request(source_floor=5, destination_floor=0, timestamp=3)
    return req_up_1, req_down_1, req_up_2, req_down_2


@pytest.fixture
def simultaneous_requests():
    """
    Create multiple requests with the same timestamp (true simultaneous requests).
    
    Returns:
        List of 5 requests all with timestamp=0
    """
    requests = []
    for i in range(5):
        source = (i % 10) + 1
        destination = (source + 3) % 10
        requests.append(Request(source_floor=source, destination_floor=destination, timestamp=0))
    return requests


def reset_request_id_counter():
    """Reset the Request ID counter for test isolation."""
    Request._id_counter = 0


@pytest.fixture(autouse=True)
def reset_request_ids():
    """Automatically reset request IDs before each test for isolation."""
    reset_request_id_counter()
    yield
    reset_request_id_counter()
