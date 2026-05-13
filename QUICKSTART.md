# Quick Start Guide

Get ElevateAI running in minutes.

## Prerequisites

- Python 3.8+ (tested on 3.8, 3.9, 3.10, 3.11, 3.14)
- pip (Python package manager)

## Installation

### 1. Clone or Download

```bash
# Download the project
unzip ElevateAI.zip
cd ElevateAI
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **pygame** (2.0+) - GUI rendering
- **pytest** (7.0+) - Testing framework
- **pytest-cov** (4.0+) - Coverage reporting

## Running the Application

### Start the Simulator

```bash
python main.py
```

The GUI will show:
- **Building visualization** with elevator shafts
- **Request indicators** (↑/↓) on floors
- **Dashboard** with metrics and controls
- **Algorithm display** (SCAN or FCFS)

### Controls

| Key | Action |
|-----|--------|
| **Space** | Generate random request |
| **↑/↓** | Scroll through floors |
| **A** | Toggle algorithm (SCAN ↔ FCFS) |
| **Escape** or **Close Window** | Exit |

## Running Tests

### Quick Validation

Verify the core modules work:

```bash
python run_test_validation.py
```

This checks:
- All core modules import correctly
- Test structure is valid
- Building and Request instantiation works

### Full Test Suite

Run all 143+ tests:

```bash
pytest tests/ -v
```

### With Coverage Report

Generate coverage metrics:

```bash
pytest tests/ --cov=core --cov=schedulers --cov-report=html
```

Open `htmlcov/index.html` to view detailed coverage.

### Run Specific Tests

```bash
# Only SCAN scheduler tests
pytest tests/test_scan_scheduler.py -v

# Only integration tests
pytest tests/test_integration.py -v

# Tests matching a pattern
pytest tests/ -k "test_request" -v
```

### Test Markers

Tests are organized with markers:

```bash
# Run only unit tests
pytest tests/ -m unit -v

# Run only integration tests
pytest tests/ -m integration -v

# Run only algorithm tests
pytest tests/ -m scheduling -v

# Skip slow tests
pytest tests/ -m "not slow" -v
```

## Troubleshooting

### ImportError: No module named 'pygame'

Install dependencies:
```bash
pip install -r requirements.txt
```

### pytest: No module named 'pytest'

The test framework isn't installed:
```bash
pip install pytest pytest-cov
```

### Tests pass but slow

Some integration tests take 5-10 seconds. This is normal for 100+ request scenarios.

```bash
# Skip slow tests
pytest tests/ -m "not slow" -v
```

### GUI doesn't appear (pygame error)

On Linux, you may need additional dependencies:
```bash
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```

## Next Steps

1. **Run the simulator** to see elevator scheduling in action
2. **Toggle algorithms** (A key) to compare SCAN vs FCFS
3. **Run the tests** to validate the implementation
4. **Check the dashboard** to understand metrics
5. **Read README.md** for architecture details

## Project Structure

```
ElevateAI/
├── main.py                 # Start here
├── core/                   # Simulation engine
├── schedulers/             # Algorithms
├── visualization/          # GUI
├── tests/                  # 143+ test cases
├── README.md               # Full documentation
├── TESTING.md              # Testing guide
└── requirements.txt        # Dependencies
```

## Performance Tips

### For Large Scenarios

- **Reduce simulation speed**: Modify `FPS` in `main.py`
- **Disable rendering**: Comment out visualization code
- **Batch requests**: Use larger time windows

### Memory Optimization

- **Limit history**: Clear old requests periodically
- **Use fewer elevators**: Start with 2-3, scale as needed
- **Shorter simulation**: Test with limited request volume

## Support & Documentation

- **README.md** - Full project documentation
- **TESTING.md** - Comprehensive testing guide
- **PROJECT_STRUCTURE.md** - Architecture & design
- **CONTRIBUTING.md** - Development guidelines

For issues or questions, check the documentation files first!
