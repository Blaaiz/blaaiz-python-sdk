#!/usr/bin/env python3
"""
Test runner for Blaaiz Python SDK

This script provides a simple way to run tests without installing pytest globally.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_command(cmd, description):
    """Run a command and report the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ SUCCESS")
        if result.stdout:
            print(result.stdout)
    else:
        print("✗ FAILED")
        if result.stderr:
            print("STDERR:", result.stderr)
        if result.stdout:
            print("STDOUT:", result.stdout)
    
    return result.returncode == 0

def main():
    """Main test runner."""
    print("Blaaiz Python SDK Test Runner")
    print("=" * 60)
    
    # Change to project directory
    os.chdir(project_root)
    
    # Check if we're in a virtual environment
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        print("WARNING: You are not in a virtual environment.")
        print("It's recommended to run tests in a virtual environment.")
        print("Create one with: python -m venv venv && source venv/bin/activate")
        print()
    
    # Run tests based on command line arguments
    test_type = sys.argv[1] if len(sys.argv) > 1 else 'all'
    
    if test_type == 'unit':
        print("Running unit tests only...")
        success = run_unit_tests()
    elif test_type == 'integration':
        print("Running integration tests only...")
        success = run_integration_tests()
    elif test_type == 'coverage':
        print("Running tests with coverage...")
        success = run_coverage_tests()
    elif test_type == 'lint':
        print("Running linting...")
        success = run_linting()
    elif test_type == 'format':
        print("Running code formatting...")
        success = run_formatting()
    elif test_type == 'all':
        print("Running all tests and checks...")
        success = run_all_tests()
    else:
        print(f"Unknown test type: {test_type}")
        print("Available options: unit, integration, coverage, lint, format, all")
        return 1
    
    return 0 if success else 1

def run_unit_tests():
    """Run unit tests."""
    try:
        import unittest
        # Discover and run unit tests
        loader = unittest.TestLoader()
        suite = loader.discover('tests', pattern='test_*.py')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except ImportError as e:
        print(f"Error importing test modules: {e}")
        return False

def run_integration_tests():
    """Run integration tests."""
    if not os.getenv('BLAAIZ_API_KEY'):
        print("WARNING: BLAAIZ_API_KEY not set. Integration tests will be skipped.")
        print("Set BLAAIZ_API_KEY environment variable to run integration tests.")
        return True
    
    try:
        import unittest
        # Run only integration tests
        suite = unittest.TestSuite()
        from tests.test_integration import TestBlaaizIntegration
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestBlaaizIntegration))
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except ImportError as e:
        print(f"Error importing integration tests: {e}")
        return False

def run_coverage_tests():
    """Run tests with coverage."""
    try:
        import coverage
        cov = coverage.Coverage()
        cov.start()
        
        # Run unit tests
        success = run_unit_tests()
        
        cov.stop()
        cov.save()
        
        print("\nCoverage Report:")
        print("=" * 60)
        cov.report()
        
        # Generate HTML report
        cov.html_report(directory='htmlcov')
        print("\nHTML coverage report generated in htmlcov/")
        
        return success
    except ImportError:
        print("Coverage package not installed. Install with: pip install coverage")
        return run_unit_tests()

def run_linting():
    """Run code linting."""
    success = True
    
    # Check if flake8 is available
    try:
        result = subprocess.run(['flake8', '--version'], capture_output=True)
        if result.returncode == 0:
            success &= run_command(['flake8', 'blaaiz/', 'tests/', 'examples/'], "Flake8 linting")
    except FileNotFoundError:
        print("flake8 not found. Install with: pip install flake8")
    
    # Check if black is available
    try:
        result = subprocess.run(['black', '--version'], capture_output=True)
        if result.returncode == 0:
            success &= run_command(['black', '--check', 'blaaiz/', 'tests/', 'examples/'], "Black formatting check")
    except FileNotFoundError:
        print("black not found. Install with: pip install black")
    
    # Check if mypy is available
    try:
        result = subprocess.run(['mypy', '--version'], capture_output=True)
        if result.returncode == 0:
            success &= run_command(['mypy', 'blaaiz/'], "MyPy type checking")
    except FileNotFoundError:
        print("mypy not found. Install with: pip install mypy")
    
    return success

def run_formatting():
    """Run code formatting."""
    try:
        result = subprocess.run(['black', '--version'], capture_output=True)
        if result.returncode == 0:
            return run_command(['black', 'blaaiz/', 'tests/', 'examples/'], "Black code formatting")
    except FileNotFoundError:
        print("black not found. Install with: pip install black")
        return False

def run_all_tests():
    """Run all tests and checks."""
    success = True
    
    print("Step 1: Running unit tests...")
    success &= run_unit_tests()
    
    print("\nStep 2: Running linting...")
    success &= run_linting()
    
    print("\nStep 3: Running integration tests...")
    success &= run_integration_tests()
    
    if success:
        print("\n🎉 All tests and checks passed!")
    else:
        print("\n❌ Some tests or checks failed.")
    
    return success

if __name__ == '__main__':
    sys.exit(main())