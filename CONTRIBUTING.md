# Contributing Guide

Thank you for contributing to ElevateAI! This guide explains how to develop and contribute to the project.

## Getting Started

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/ElevateAI.git
cd ElevateAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies including dev tools
pip install -r requirements.txt

# Verify setup
python run_test_validation.py
```

### Project Structure Overview

```
core/        - Simulation engine (building, elevator, request, metrics)
schedulers/  - Algorithms (base, FCFS, SCAN)
visualization/ - GUI (pygame rendering)
tests/       - Test suite (143+ tests)
main.py      - Application entry point
```

## Development Workflow

### 1. Before You Code

- **Read the documentation**: README.md, TESTING.md, PROJECT_STRUCTURE.md
- **Understand the architecture**: Review core modules
- **Check existing code**: Avoid duplicating functionality
- **Plan your changes**: Design before implementing

### 2. Creating New Features

#### Adding a New Scheduler Algorithm

1. **Create the scheduler class**
   ```python
   # schedulers/my_scheduler.py
   from schedulers.base_scheduler import BaseScheduler
   from core.request import Request
   
   class MyScheduler(BaseScheduler):
       def schedule(self, current_time: int) -> None:
           """Your scheduling algorithm here."""
           pass
   ```

2. **Implement the schedule() method**
   - Use `self.get_pending_requests()` to get unassigned requests
   - Use `self.assign_request_to_elevator(request, elevator)` to assign
   - Consider direction, distance, and load

3. **Add tests**
   ```python
   # tests/test_my_scheduler.py
   import pytest
   from schedulers.my_scheduler import MyScheduler
   
   class TestMyScheduler:
       def test_basic_scheduling(self, building):
           scheduler = MyScheduler(building)
           # Your tests here
   ```

4. **Update main.py to support the algorithm**
   ```python
   elif algorithm_choice == 'my':
       scheduler = MyScheduler(building)
   ```

5. **Run tests**
   ```bash
   pytest tests/test_my_scheduler.py -v
   ```

#### Adding a New Metric

1. **Define the metric in core/metrics.py**
2. **Implement tracking in Elevator or Building**
3. **Add visualization in visualization/pygame_view.py**
4. **Create tests in tests/test_*.py**

#### Fixing a Bug

1. **Create a minimal test that reproduces the bug**
2. **Fix the bug**
3. **Verify the test passes**
4. **Check no other tests broke**
5. **Submit PR with test + fix**

### 3. Code Standards

#### Style Guide

- **PEP 8**: Follow Python style guidelines
- **Type hints**: Use for function signatures
- **Docstrings**: Document all public methods
- **Comments**: Explain "why", not "what"

Example:

```python
def assign_request(self, request: Request) -> None:
    """
    Assign a passenger request to this elevator.
    
    Args:
        request (Request): The request to assign.
        
    Raises:
        ValueError: If elevator is at capacity.
    """
    if len(self.active_requests) >= self.capacity:
        raise ValueError("Elevator at capacity")
    
    self.active_requests.append(request)
    request.assigned_elevator_id = self.id
```

#### Import Order

```python
# 1. Standard library
import sys
from typing import List
from abc import ABC, abstractmethod

# 2. Third-party
import pygame

# 3. Local application
from core.building import Building
from schedulers.base_scheduler import BaseScheduler
```

#### Naming Conventions

- **Classes**: PascalCase (`ElevatorScheduler`)
- **Functions/Methods**: snake_case (`assign_request()`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_CAPACITY = 10`)
- **Private**: Leading underscore (`_internal_method()`)

### 4. Testing

#### Test Organization

- **Unit tests**: Single component isolation
- **Integration tests**: Multiple components together
- **Test markers**: Label tests with @pytest.mark

```python
import pytest

@pytest.mark.unit
def test_elevator_state_change():
    """Test single elevator state transition."""
    pass

@pytest.mark.integration
def test_full_request_flow(building):
    """Test end-to-end request handling."""
    pass

@pytest.mark.scheduling
def test_scheduler_fairness(scan_scheduler):
    """Test algorithm fairness metrics."""
    pass

@pytest.mark.slow
def test_large_scale_scenario():
    """Test with 100+ requests (may take 10s)."""
    pass
```

#### Writing Tests

Use the Arrange-Act-Assert pattern:

```python
def test_elevator_moves_up(small_building):
    """Elevator should move up when assigned higher floor."""
    # Arrange
    elevator = small_building.elevators[0]
    target_floor = 5
    
    # Act
    elevator.target_floor = target_floor
    elevator.move_up()
    elevator.step()
    
    # Assert
    assert elevator.current_floor == 1  # Moves one floor
    assert elevator.state == "MOVING_UP"
```

#### Test Fixtures

Use fixtures from `tests/conftest.py`:

```python
def test_with_fixtures(small_building, fcfs_scheduler, simple_request):
    """Use pre-configured fixtures."""
    # small_building: 5 floors, 2 elevators
    # fcfs_scheduler: Configured for small_building
    # simple_request: Request from floor 2 to 4
    pass
```

#### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_elevator.py -v

# Tests matching pattern
pytest tests/ -k "state" -v

# With coverage
pytest tests/ --cov=core --cov=schedulers --cov-report=html

# Only unit tests
pytest tests/ -m unit -v

# Exclude slow tests
pytest tests/ -m "not slow" -v
```

### 5. Before Submitting PR

**Checklist:**

- [ ] Code follows PEP 8 style
- [ ] All functions/classes have docstrings
- [ ] Type hints included
- [ ] New tests added for new features
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage maintained: `pytest tests/ --cov=core --cov=schedulers`
- [ ] No debug prints left in code
- [ ] Commit messages are clear and descriptive
- [ ] Documentation updated if needed

**Run before submitting:**

```bash
# Full validation
pytest tests/ -v --cov=core --cov=schedulers --cov-report=term-missing

# Style check (if you have pylint/flake8)
pylint core/ schedulers/ tests/
```

## Pull Request Process

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

- Keep changes focused on one feature
- Write tests alongside code
- Commit frequently with clear messages

```bash
git add .
git commit -m "Add new scheduler with scoring heuristics"
```

### 3. Run Full Test Suite

```bash
pytest tests/ -v --cov=core --cov=schedulers
```

Ensure:
- All new tests pass
- No existing tests broke
- Coverage maintained (>85%)

### 4. Push and Create PR

```bash
git push origin feature/my-feature
```

### 5. PR Description

Include:
- **What**: What does this PR do?
- **Why**: Why is this change needed?
- **How**: How does it work?
- **Testing**: What tests were added/modified?
- **Checklist**: Confirm you followed guidelines

Example:

```markdown
## What
Implement SSTF (Shortest Seek Time First) scheduler

## Why
Better responsiveness for close-proximity requests

## Testing
- Added 25 unit tests for SSTF logic
- Added 5 integration tests
- All existing tests pass
- Coverage: 92% (up from 90%)

- [x] Code follows style guide
- [x] Tests added
- [x] No breaking changes
```

## Code Review

### Reviewing Others' Code

- **Be constructive**: Offer solutions, not just criticism
- **Check logic**: Do the algorithms work correctly?
- **Test coverage**: Are new features tested?
- **Style**: Does it follow our guidelines?
- **Performance**: Could it be optimized?

### Responding to Reviews

- Acknowledge feedback
- Ask questions if unclear
- Make requested changes
- Respond to all comments
- Request re-review when done

## Reporting Bugs

### Bug Report Template

```markdown
## Description
Brief description of the bug

## Steps to Reproduce
1. Start the simulator
2. Create 10 requests
3. Toggle to SCAN algorithm
...

## Expected Behavior
Elevators should distribute evenly

## Actual Behavior
All requests go to one elevator

## Environment
- OS: Windows 10
- Python: 3.10
- pygame: 2.1.0
```

## Feature Requests

### Feature Request Template

```markdown
## Use Case
Describe the problem you're trying to solve

## Proposed Solution
How should this work?

## Alternatives Considered
Any other approaches?

## Example
Show how you'd use it

## Impact
What's the benefit?
```

## Questions & Discussion

- **GitHub Issues**: For bugs and feature discussions
- **Documentation**: Check TESTING.md and README.md first
- **Code Comments**: Ask questions in PR reviews

## License

By contributing, you agree your code is licensed under the MIT License.

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md
- GitHub "Contributors" page
- Project documentation

---

Thank you for contributing to ElevateAI! 🎉
