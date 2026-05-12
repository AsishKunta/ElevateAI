# ElevateAI

> Real-time elevator scheduling and optimization simulator  
> implementing FCFS and SCAN scheduling algorithms with live visualization,  
> multi-elevator dispatching, and performance metrics.
---

## Demo

<img width="892" height="558" alt="image" src="https://github.com/user-attachments/assets/76b191a8-fe40-4381-9418-8858eb92f518" />


---

# Overview

ElevateAI is a systems-oriented simulation project focused on real-time elevator scheduling, dispatch optimization, fairness, and efficiency analysis.

The simulator models a multi-elevator enterprise building environment where elevators dynamically respond to passenger requests while minimizing:

* Average wait time
* Unnecessary travel distance
* Idle movement
* Direction reversals
* Scheduling inefficiencies

The project was designed to explore core concepts used in:

* Operating systems scheduling
* Resource allocation systems
* Real-time simulation engines
* Optimization algorithms
* State-machine-driven architectures
* Event-driven systems

Unlike traditional CRUD portfolio projects, ElevateAI focuses on algorithmic behavior, scheduling intelligence, simulation architecture, and measurable optimization.

---

# Key Features

## Real-Time Simulation

* Live elevator movement simulation
* Multi-floor building environment
* Dynamic passenger request generation
* Real-time state updates

## Scheduling Algorithms

* FCFS (First Come First Serve)
* SCAN (Elevator Algorithm)
* Runtime scheduler switching
* Request batching and directional optimization

## Multi-Elevator Dispatching

* Multiple autonomous elevator agents
* Dynamic request assignment
* Direction-aware scheduling
* Idle elevator management

## Metrics Dashboard

Tracks live system performance metrics including:

* Average wait time
* Total travel distance
* Idle time
* Efficiency score
* Active requests
* Completed requests

## Visualization

* Interactive Pygame visualization
* Elevator state rendering
* Floor request indicators
* Real-time dashboard updates

## State Machine Architecture

Explicit elevator states:

* IDLE
* MOVING_UP
* MOVING_DOWN
* PICKING_UP
* DROPPING_OFF

---

# System Architecture

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
├── main.py
└── test_simulation.py
```

---

# Scheduling Algorithms

## FCFS (First Come First Serve)

The FCFS scheduler processes requests sequentially in the order they arrive.

Characteristics:

* Simple scheduling logic
* Reactive request handling
* Frequent direction reversals
* Lower optimization efficiency

Used primarily as a baseline scheduling strategy.

---

## SCAN (Elevator Algorithm)

The SCAN scheduler improves scheduling efficiency by keeping elevators moving in the current direction while batching compatible requests before reversing.

Key behaviors:

* Direction persistence
* Request batching
* Reduced unnecessary reversals
* Better travel efficiency
* Lower average wait times

This algorithm is conceptually similar to disk scheduling strategies used in operating systems.

---

# Metrics and Optimization

ElevateAI continuously tracks simulation performance using live metrics.

| Metric             | Purpose                               |
| ------------------ | ------------------------------------- |
| Average Wait Time  | Measures passenger waiting efficiency |
| Travel Distance    | Measures total elevator movement      |
| Idle Time          | Measures unused elevator time         |
| Efficiency Score   | Estimates overall scheduling quality  |
| Completed Requests | Measures throughput                   |
| Active Requests    | Measures current system load          |

These metrics allow direct comparison between scheduling algorithms.

---

# Engineering Challenges Solved

## Modular Scheduler Architecture

Designed a pluggable scheduling system allowing runtime switching between FCFS and SCAN algorithms.

## Deterministic Elevator State Machine

Implemented explicit elevator states to eliminate inconsistent movement behavior and stale state transitions.

## Real-Time Simulation Loop

Built a synchronized simulation engine supporting live movement, request handling, rendering, and metrics updates.

## Direction-Aware Scheduling

Implemented SCAN scheduling logic to reduce inefficient reversals and improve batching efficiency.

## Visualization and Observability

Created a live dashboard exposing scheduling metrics and elevator states for easier debugging and performance analysis.

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

## Live Simulation Dashboard

<img width="896" height="565" alt="image" src="https://github.com/user-attachments/assets/28192f69-aee7-42ba-90b9-9dd745673e9b" />


---

## SCAN Scheduling Visualization

<img width="1800" height="1126" alt="image" src="https://github.com/user-attachments/assets/c63a56b6-068c-4bc5-9592-b70297255643" />


---

# Technologies Used

* Python
* Pygame
* Object-Oriented Programming
* Scheduling Algorithms
* Real-Time Simulation
* Event-Driven Architecture

---

# Run Locally

## Clone Repository

```bash
git clone https://github.com/AsishKunta/ElevateAI.git
cd ElevateAI
```

## Install Dependencies

```bash
pip install pygame
```

## Run Simulation

```bash
py -3.12 main.py
```

---

# Future Work

* Peak-hour traffic simulation
* Congestion modeling
* Smart idle positioning
* Predictive traffic estimation
* Intelligent traffic prediction experiments
* Advanced efficiency analytics

---

# Author

**Asish Kunta**
GitHub: [https://github.com/AsishKunta](https://github.com/AsishKunta)
