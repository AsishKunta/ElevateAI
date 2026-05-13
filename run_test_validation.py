#!/usr/bin/env python3
"""
Simple test runner to verify test suite structure without pytest installed.

This validates:
- Test files compile correctly
- Fixtures can be imported
- Test classes and methods are properly defined
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def validate_test_structure():
    """Validate that all test files have correct structure."""
    
    print("=" * 70)
    print("ELEVATEAI TEST SUITE VALIDATION")
    print("=" * 70)
    
    # Import test modules
    test_modules = [
        ('tests.conftest', 'conftest.py - Fixtures & Setup'),
        ('tests.test_request', 'test_request.py - Request Tests'),
        ('tests.test_building', 'test_building.py - Building Tests'),
        ('tests.test_elevator', 'test_elevator.py - Elevator Tests'),
        ('tests.test_fcfs_scheduler', 'test_fcfs_scheduler.py - FCFS Tests'),
        ('tests.test_scan_scheduler', 'test_scan_scheduler.py - SCAN Tests'),
        ('tests.test_integration', 'test_integration.py - Integration Tests'),
    ]
    
    passed = 0
    failed = 0
    
    for module_name, description in test_modules:
        try:
            __import__(module_name)
            print(f"✓ {description:<50} PASS")
            passed += 1
        except Exception as e:
            print(f"✗ {description:<50} FAIL: {str(e)[:40]}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"MODULE VALIDATION: {passed} passed, {failed} failed")
    print("=" * 70)
    
    # Count test classes and functions
    try:
        from tests import test_request, test_building, test_elevator
        from tests import test_fcfs_scheduler, test_scan_scheduler, test_integration
        
        test_modules_obj = [
            test_request, test_building, test_elevator,
            test_fcfs_scheduler, test_scan_scheduler, test_integration
        ]
        
        total_test_classes = 0
        total_test_methods = 0
        
        for module in test_modules_obj:
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and name.startswith('Test'):
                    total_test_classes += 1
                    for method_name in dir(obj):
                        if method_name.startswith('test_'):
                            total_test_methods += 1
        
        print(f"\nTEST STRUCTURE:")
        print(f"  Test Classes:  {total_test_classes}")
        print(f"  Test Methods:  {total_test_methods}")
        print(f"  Total Tests:   Approximately {total_test_methods}")
        
    except Exception as e:
        print(f"\nCould not count tests: {e}")
    
    print("\n" + "=" * 70)
    print("TEST SUITE READY FOR PYTEST")
    print("=" * 70)
    print("\nTo run tests, install pytest and run:")
    print("  pip install pytest pytest-cov")
    print("  pytest tests/ -v")
    print("\nFor coverage report:")
    print("  pytest tests/ --cov=core --cov=schedulers --cov-report=html")
    print("=" * 70)
    
    return failed == 0


def verify_imports():
    """Verify core modules can be imported."""
    print("\n" + "=" * 70)
    print("VERIFYING CORE MODULE IMPORTS")
    print("=" * 70)
    
    try:
        from core.request import Request
        from core.building import Building
        from core.elevator import Elevator
        from schedulers.base_scheduler import BaseScheduler
        from schedulers.fcfs_scheduler import FCFSScheduler
        from schedulers.scan_scheduler import SCANScheduler
        
        print("✓ core.request")
        print("✓ core.building")
        print("✓ core.elevator")
        print("✓ schedulers.base_scheduler")
        print("✓ schedulers.fcfs_scheduler")
        print("✓ schedulers.scan_scheduler")
        
        # Quick sanity check
        building = Building(num_floors=10, num_elevators=2)
        req = Request(source_floor=2, destination_floor=8, timestamp=0)
        
        print("\n✓ Building instantiation successful")
        print("✓ Request instantiation successful")
        print("\n" + "=" * 70)
        print("ALL CORE IMPORTS VERIFIED")
        print("=" * 70)
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


if __name__ == "__main__":
    success = verify_imports()
    success = validate_test_structure() and success
    
    sys.exit(0 if success else 1)
