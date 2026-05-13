"""
TESTING GUIDE FOR ELEVATEAI

This document provides comprehensive testing information for the ElevateAI project.

## Quick Start

Run all tests:
    pytest tests/ -v

Run with coverage:
    pytest tests/ --cov=core --cov=schedulers --cov-report=html

Run specific test file:
    pytest tests/test_elevator.py -v

## Test Suite Organization

### 1. Unit Tests

#### test_request.py (20 tests)
Tests the Request lifecycle and state management.

Key scenarios:
- Request creation with proper initialization
- Direction inference (UP/DOWN)
- State transitions (pending → assigned → picked_up → completed)
- ID generation and uniqueness
- Timestamp tracking
- Edge cases (same source/destination, negative floors)

Why these matter:
- Requests are fundamental to the simulation
- Correct direction inference affects scheduling efficiency
- State management ensures scheduler correctness

Run: pytest tests/test_request.py -v

#### test_building.py (20+ tests)
Tests the Building class and building-wide operations.

Key scenarios:
- Building initialization with correct floor/elevator counts
- Request queue management (pending vs. history)
- Elevator access and coordination
- Simulation stepping and event generation
- Building status reporting

Why these matter:
- Building is the central coordinator
- Correct queue management prevents request loss
- Building.has_work() determines simulation termination

Run: pytest tests/test_building.py -v

#### test_elevator.py (35+ tests)
Tests the Elevator state machine and movement logic.

Key scenarios:
- Movement (UP/DOWN) with floor tracking
- State transitions (IDLE → MOVING → PICKING_UP → DROPPING_OFF)
- Request assignment and pickup/dropoff mechanics
- Target selection after arrivals
- Distance and idle time tracking

Why these matter:
- Elevator state machine is the core of simulation accuracy
- State transitions must be deterministic
- Proper target selection affects efficiency

Run: pytest tests/test_elevator.py -v

### 2. Algorithm Tests

#### test_fcfs_scheduler.py (25+ tests)
Tests First-Come-First-Served scheduling algorithm.

Key scenarios:
- Requests processed in arrival order
- Nearest idle elevator selection
- Direction compatibility scoring
- Load balancing heuristics
- Handling empty/full queues
- Multi-step simulation

Why these matter:
- FCFS is the baseline algorithm
- Scoring heuristics affect assignment quality
- Must work reliably in all conditions

Run: pytest tests/test_fcfs_scheduler.py -v

#### test_scan_scheduler.py (30+ tests)
Tests SCAN elevator scheduling algorithm.

Key scenarios:
- Same-direction request batching
- Direction persistence until requests exhausted
- Idle elevator initialization
- SCAN-specific scoring heuristics
- Comparison with FCFS efficiency
- Complete simulation flows

Why these matter:
- SCAN is the optimized algorithm
- Direction persistence is key differentiator
- Must demonstrate efficiency improvements

Run: pytest tests/test_scan_scheduler.py -v

### 3. Integration Tests

#### test_integration.py (20+ tests)
Tests complete end-to-end simulation scenarios.

Key scenarios:
- Single/multiple request completion
- Concurrent request handling
- Capacity and overload conditions
- Scheduler comparison
- Real-world usage patterns (morning rush, evening dispersal)
- Long-running stability

Why these matter:
- Validates entire system works together
- Catches interaction bugs unit tests miss
- Ensures production readiness

Run: pytest tests/test_integration.py -v

## Test Markers

Tests can be organized by category:

```bash
# Run only scheduling tests
pytest tests/ -m scheduling

# Run only integration tests
pytest tests/ -m integration

# Skip slow tests
pytest tests/ -m "not slow"
```

## Coverage Report

Generate HTML coverage report:

    pytest tests/ --cov=core --cov=schedulers --cov-report=html
    open htmlcov/index.html

Expected coverage:
- Core modules: >90%
- Schedulers: >85%
- Visualization: >60% (harder to test GUI code)

## Important Test Patterns

### 1. Fixtures (conftest.py)
Reusable test setup:

```python
@pytest.fixture
def medium_building():
    """Create a building with 10 floors and 3 elevators."""
    return Building(num_floors=10, num_elevators=3)
```

Fixtures ensure:
- Consistent test environment
- No state leakage between tests
- Request ID counter reset

### 2. Request ID Isolation
Request class has global ID counter that must be reset:

```python
@pytest.fixture(autouse=True)
def reset_request_ids():
    """Automatically reset IDs before each test."""
    Request._id_counter = 0
    yield
    Request._id_counter = 0
```

### 3. Simulation Stepping
Most complex scenarios require step loops:

```python
for step in range(100):
    scheduler.schedule(current_time=step)
    building.step(current_time=step)
    if all(req.completed for req in requests):
        break
assert all(req.completed for req in requests)
```

## Failing Tests: Diagnosis

### Test: test_elevator.py::TestElevatorState::test_picking_up_state_on_pickup

**What it tests:** Elevator state transitions to PICKING_UP on arrival

**Why it might fail:**
- Elevator.step() not calling _handle_arrival()
- State not being set to PICKING_UP
- Request not marked picked_up

**How to debug:**
1. Check Elevator.step() calls _handle_arrival()
2. Check _handle_arrival() sets state = "PICKING_UP"
3. Verify request.picked_up = True in _handle_arrival()

### Test: test_fcfs_scheduler.py::TestFCFSScheduling::test_fcfs_assigns_requests_in_arrival_order

**What it tests:** FCFS assigns requests in timestamp order

**Why it might fail:**
- Sorting by timestamp not working
- Assignment removing request from pending incorrectly
- Missing requests in assignment

**How to debug:**
1. Print pending_requests after sorting
2. Verify each request gets assigned
3. Check requests removed from pending_requests

### Test: test_scan_scheduler.py::TestSCANDirectionPersistence::test_scan_batches_same_direction_requests

**What it tests:** SCAN batches compatible requests together

**Why it might fail:**
- _batch_requests_for_elevator() not finding compatible requests
- Direction comparison broken
- Request assignment not happening

**How to debug:**
1. Check elevator.direction is 1 (UP)
2. Verify requests have direction == 1
3. Check _batch_requests_for_elevator() logic

## Running Specific Test Scenarios

### Test a single component thoroughly
```bash
pytest tests/test_elevator.py -v
```

### Test scheduling correctness
```bash
pytest tests/test_fcfs_scheduler.py tests/test_scan_scheduler.py -v
```

### Test a specific scenario
```bash
pytest tests/test_integration.py::TestRealWorldScenarios::test_morning_rush_scenario -v
```

### Test with print statements for debugging
```bash
pytest tests/test_elevator.py::TestElevatorMovement::test_move_up_increments_floor -v -s
```

## Performance Testing

To profile test performance:

```bash
pytest tests/ --durations=10
```

This shows the 10 slowest tests.

## Continuous Integration

GitHub Actions runs tests on:
- Python 3.8, 3.9, 3.10, 3.11
- Linux (Ubuntu latest)

Workflow: `.github/workflows/tests.yml`

Tests must pass on all versions before code merge.

## Best Practices for Adding New Tests

1. **Test One Thing**: Each test should verify single behavior
2. **Clear Names**: Test name should describe what it tests
3. **Arrange-Act-Assert**: Setup → Execute → Verify
4. **Use Fixtures**: Reuse setup code via pytest fixtures
5. **Add Comments**: Explain why test matters
6. **Test Edge Cases**: Empty queues, single item, maximum load
7. **Avoid Flakiness**: No random delays, deterministic setup

Example:

```python
def test_elevator_picks_up_passenger(self):
    """
    Verify elevator transitions to PICKING_UP state and marks 
    request as picked_up when reaching source floor.
    
    This matters because:
    - Pickup state must be immediately visible to visualization
    - Request must be marked picked_up to avoid double pickup
    - Ensures correct state machine transitions
    """
    # Arrange
    elevator = Elevator(elevator_id=0)
    req = Request(source_floor=2, destination_floor=8, timestamp=0)
    elevator.assign_request(req)
    
    # Act
    elevator.current_floor = 2
    elevator.step(current_time=0)
    
    # Assert
    assert elevator.state == "PICKING_UP"
    assert req.picked_up
```

## Test Maintenance

### When to Update Tests

- When changing API (method signatures)
- When fixing bugs (add test for bug first)
- When adding features (add test before feature)
- When optimizing (ensure test still passes)

### When to Add More Tests

- New failure mode discovered
- Edge case not covered
- Performance regression
- New code path added

## Troubleshooting

### Tests fail with "ModuleNotFoundError"
- Ensure working directory is project root
- Install with: `pip install -e .`

### Tests pass locally but fail in CI
- Check Python version differences
- Verify dependencies in requirements.txt
- Look for OS-specific issues

### Specific test is flaky
- Likely has timing dependency or global state
- Add print statements to debug
- Check for fixture isolation issues

### Coverage is low on visualization
- GUI code is hard to test programmatically
- Consider refactoring GUI logic into testable units
- Focus coverage on core/schedulers first

## See Also

- Main README: architecture, features, usage
- Code documentation: docstrings in source files
- GitHub Actions: `.github/workflows/tests.yml`
"""
