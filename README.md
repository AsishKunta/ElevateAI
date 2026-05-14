# ElevateAI

### Real-Time Elevator Scheduling & Optimization Simulator

ElevateAI is a systems-oriented simulation project focused on real-time elevator scheduling, dispatch optimization, fairness, and efficiency analysis.

The project simulates a multi-elevator building environment where elevators dynamically respond to passenger requests while minimizing:

* Passenger wait time
* Unnecessary travel distance
* Idle movement
* Direction reversals
* Scheduling inefficiencies

Unlike traditional CRUD portfolio projects, ElevateAI focuses on scheduling algorithms, simulation architecture, state-machine-driven systems, and measurable optimization behavior.

---

# Demo

## Live Simulation Dashboard

<img width="896" height="565" alt="image" src="https://github.com/user-attachments/assets/28192f69-aee7-42ba-90b9-9dd745673e9b" />

---

# Core Features

## Real-Time Simulation

* Live multi-elevator movement simulation
* Dynamic passenger request generation
* Real-time elevator state updates
* Event-driven request handling

## Scheduling Algorithms

* FCFS (First Come First Serve)
* SCAN (Elevator Algorithm)
* Runtime scheduler switching
* Direction-aware request batching

## Multi-Elevator Dispatching

* Multiple autonomous elevator agents
* Dynamic request assignment
* Direction-aware scheduling decisions
* Idle elevator management

## Metrics Tracking

Tracks live simulation metrics including:

* Average wait time
* Total elevator travel distance
* Idle time
* Active requests
* Completed requests
* Overall efficiency score

## Visualization

* Interactive Pygame visualization
* Real-time elevator rendering
* Floor request indicators
* Live scheduling dashboard

---

# Elevator State Machine

Elevators operate using explicit state transitions:

* IDLE
* MOVING_UP
* MOVING_DOWN
* PICKING_UP
* DROPPING_OFF

This architecture helps maintain deterministic movement behavior and consistent request lifecycle handling.

---

# # System Architecture

```text
┌──────────────────┐
│  User Requests   │
└────────┬─────────┘
         ↓
┌──────────────────┐
│  Request Queue   │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Scheduler Engine │
│ FCFS / SCAN      │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Elevator Manager │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Simulation Core  │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Metrics & Logs   │
└──────────────────┘
```

# Project Structure

```text
ElevateAI/
│
├── core/
│   ├── building.py
│   ├── elevator.py
│   ├── request.py
│   └── metrics.py
│
├── schedulers/
│   ├── base_scheduler.py
│   ├── fcfs_scheduler.py
│   └── scan_scheduler.py
│
├── visualization/
│   └── pygame_view.py
│
├── tests/
│   ├── integration tests
│   ├── scheduler validation tests
│   ├── elevator state tests
│   └── edge-case handling tests
│
├── .github/workflows/
│   └── tests.yml
│
├── main.py
└── requirements.txt
```

---

# Scheduling Algorithms

## FCFS (First Come First Serve)

Processes elevator requests sequentially in the order they arrive.

Characteristics:

* Simple request handling
* Reactive scheduling behavior
* Higher direction reversals
* Baseline scheduling strategy

---

## SCAN (Elevator Algorithm)

Improves scheduling efficiency by continuing movement in the current direction while batching compatible requests before reversing.

Characteristics:

* Direction persistence
* Reduced unnecessary reversals
* Improved request batching
* Lower average travel overhead
* Better scheduling efficiency

The SCAN strategy is conceptually similar to disk scheduling algorithms used in operating systems.

---

# Metrics and Optimization

ElevateAI continuously tracks simulation performance metrics to compare scheduling behavior across algorithms.

| Metric             | Description                           |
| ------------------ | ------------------------------------- |
| Average Wait Time  | Measures passenger waiting efficiency |
| Travel Distance    | Tracks total elevator movement        |
| Idle Time          | Measures unused elevator time         |
| Efficiency Score   | Estimates overall scheduling quality  |
| Active Requests    | Measures current system load          |
| Completed Requests | Measures throughput                   |

---

# Automated Testing & CI/CD

ElevateAI includes automated testing and scheduler validation using `pytest`.

The test suite validates:

* FCFS scheduling behavior
* SCAN direction persistence
* Request lifecycle tracking
* Multi-elevator coordination
* Timestamp-aware scheduling
* Scheduler scoring logic
* Elevator state transitions
* Integration and edge-case scenarios

GitHub Actions automatically executes the test suite on every push and pull request.

Current test coverage includes:

* Unit tests
* Scheduler validation tests
* Integration tests
* Edge-case simulation tests

---

# Engineering Challenges Solved

## Modular Scheduler Architecture

Designed a pluggable scheduling framework allowing runtime switching between FCFS and SCAN algorithms.

## Deterministic Elevator State Machine

Implemented explicit elevator states to prevent inconsistent movement behavior and stale transitions.

## Event-Driven Simulation Flow

Built a synchronized simulation engine handling movement, scheduling, rendering, and metrics updates in real time.

## Direction-Aware Scheduling

Implemented SCAN scheduling logic to reduce unnecessary reversals and improve batching efficiency.

## Scheduler Validation

Added automated tests and CI/CD workflows to validate scheduling correctness and simulation behavior.

---

# Controls

| Key   | Action                       |
| ----- | ---------------------------- |
| A     | Toggle FCFS / SCAN           |
| U     | Generate random UP request   |
| D     | Generate random DOWN request |
| SPACE | Pause / Resume simulation    |
| ESC   | Exit simulation              |

---

# Screenshots

## Live Dashboard

<img width="896" height="565" alt="image" src="https://github.com/user-attachments/assets/28192f69-aee7-42ba-90b9-9dd745673e9b" />

---

## SCAN Scheduling Visualization

<img width="1800" height="1126" alt="image" src="https://github.com/user-attachments/assets/c63a56b6-068c-4bc5-9592-b70297255643" />

---

# Technologies & Concepts

* Python
* Pygame
* Object-Oriented Programming
* Event-Driven Simulation
* Scheduling Algorithms
* State-Machine Architecture
* Automated Testing with pytest
* GitHub Actions CI/CD
* Real-Time Systems Simulation

---

# Run Locally

## Clone Repository

```bash
git clone https://github.com/AsishKunta/ElevateAI.git
cd ElevateAI
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Simulation

```bash
python main.py
```

## Run Tests

```bash
python -m pytest tests/ -v
```

---

# Future Improvements

* Peak-hour traffic simulation
* Congestion-aware dispatching
* Smart idle elevator positioning
* Adaptive scheduling strategies
* Traffic heatmap visualization
* Advanced scheduler benchmarking

---

# Author

**Asish Kunta**
GitHub: [https://github.com/AsishKunta](https://github.com/AsishKunta)
