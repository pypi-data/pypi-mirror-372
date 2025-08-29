#!/usr/bin/env python3
"""
Test runner for SADI Python unit tests.

This script runs different test suites based on available dependencies.
"""

import importlib.util
import os
import subprocess
import sys


def check_dependency(module_name):
    """Check if a Python module is available."""
    spec = importlib.util.find_spec(module_name)
    return spec is not None


def run_compatibility_tests():
    """Run Python 3.12 compatibility tests (no external dependencies required)."""
    print("Running Python 3.12 compatibility tests...")
    result = subprocess.run(
        [sys.executable, "test_compatibility.py"], capture_output=True, text=True
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


def run_smoke_tests():
    """Run basic smoke tests."""
    print("Running basic smoke tests...")
    result = subprocess.run(
        [sys.executable, "test_smoke.py"], capture_output=True, text=True
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


def run_comprehensive_tests():
    """Run comprehensive SADI tests (requires dependencies)."""
    print("Running comprehensive SADI tests...")
    result = subprocess.run(
        [sys.executable, "test_sadi_comprehensive.py"], capture_output=True, text=True
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


def run_original_tests():
    """Run the original test suite."""
    print("Running original SADI tests...")
    result = subprocess.run(
        [sys.executable, "tests.py"], capture_output=True, text=True
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


def check_dependencies():
    """Check what dependencies are available."""
    deps = {
        "rdflib": check_dependency("rdflib"),
        "werkzeug": check_dependency("werkzeug"),
        "webob": check_dependency("webob"),
        "sadi": check_dependency("sadi"),
    }

    print("Dependency Status:")
    for dep, available in deps.items():
        status = "✅ Available" if available else "❌ Missing"
        print(f"  {dep}: {status}")

    return all(deps.values())


def main():
    """Main test runner."""
    print("SADI Python Test Runner")
    print("=" * 50)

    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    all_passed = True

    # Always run compatibility tests first (no dependencies required)
    print("\n1. Python 3.12 Compatibility Tests")
    print("-" * 35)
    if not run_compatibility_tests():
        all_passed = False
        print("❌ Compatibility tests failed!")
    else:
        print("✅ Compatibility tests passed!")

    # Check dependencies
    print("\n2. Dependency Check")
    print("-" * 18)
    deps_available = check_dependencies()

    if deps_available:
        print("\n3. Basic Smoke Tests")
        print("-" * 20)
        if not run_smoke_tests():
            all_passed = False
            print("❌ Smoke tests failed!")
        else:
            print("✅ Smoke tests passed!")

        print("\n4. Comprehensive SADI Tests")
        print("-" * 27)
        if not run_comprehensive_tests():
            all_passed = False
            print("❌ Comprehensive tests failed!")
        else:
            print("✅ Comprehensive tests passed!")

        print("\n5. Original Test Suite")
        print("-" * 20)
        if not run_original_tests():
            all_passed = False
            print("❌ Original tests failed!")
        else:
            print("✅ Original tests passed!")
    else:
        print("\n⚠️  Skipping comprehensive tests due to missing dependencies.")
        print("To install dependencies, run:")
        print("  pip install -e .")
        print("or:")
        print("  pip install rdflib werkzeug webob python-dateutil pytidylib")

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All available tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
