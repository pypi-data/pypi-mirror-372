#!/usr/bin/env python3
"""
Standalone test runner for testing Python 3.12 compatibility.
This can run without external dependencies to verify basic compatibility.
"""

import ast
import os
import re
import sys
import unittest
from pathlib import Path


class TestPython312CompatibilityStandalone(unittest.TestCase):
    """Test Python 3.12 compatibility without external dependencies."""

    skip_paths = ["venv", "test", ".eggs", "ez_setup"]

    def get_python_files(self):
        """Get all Python files in the SADI project."""
        sadi_dir = Path(__file__).parent
        python_files = []

        for pattern in ["**/*.py"]:
            python_files.extend(sadi_dir.glob(pattern))

        return [
            f
            for f in python_files
            if f.is_file() and not any(skip in str(f) for skip in self.skip_paths)
        ]

    def test_no_buffer_function_calls(self):
        """Verify no buffer() function calls exist in the source code."""
        python_files = self.get_python_files()
        buffer_usages = []

        for filepath in python_files:
            # Skip test files, .eggs directory, and setup files
            str_path = str(filepath)
            if any(skip in str_path for skip in self.skip_paths):
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Look for buffer( calls (not in comments)
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if line.strip().startswith("#"):
                        continue
                    if re.search(r"\bbuffer\s*\(", line):
                        buffer_usages.append(str(filepath))
                        break
            except (UnicodeDecodeError, OSError):
                continue

        self.assertEqual(
            len(buffer_usages), 0, f"Found buffer() calls in: {buffer_usages}"
        )

    def test_no_future_library_imports(self):
        """Verify future library imports have been removed from source code."""
        python_files = self.get_python_files()
        future_imports = []

        deprecated_imports = [
            "from future import standard_library",
            "from builtins import str",
            "from builtins import object",
            "standard_library.install_aliases()",
        ]

        for filepath in python_files:
            # Skip test files, .eggs directory, and setup files
            str_path = str(filepath)
            if any(skip in str_path for skip in self.skip_paths):
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Look for deprecated imports (not in comments)
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if line.strip().startswith("#"):
                        continue
                    for deprecated_import in deprecated_imports:
                        if deprecated_import in line:
                            future_imports.append(f"{filepath}: {deprecated_import}")
            except (UnicodeDecodeError, OSError):
                continue

        self.assertEqual(
            len(future_imports), 0, f"Found deprecated future imports: {future_imports}"
        )

    def test_no_deprecated_constructs_usage(self):
        """Verify deprecated Python 2 constructs have been replaced."""
        python_files = self.get_python_files()
        deprecated_usages = []

        for filepath in python_files:
            # Skip test files, .eggs directory, and setup files
            str_path = str(filepath)
            if any(skip in str_path for skip in self.skip_paths):
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Look for deprecated usage (excluding comments)
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    # Skip comments
                    if line.strip().startswith("#"):
                        continue
                    if "basestring" in line:
                        deprecated_usages.append(f"{filepath}:{i}: {line.strip()}")
            except (UnicodeDecodeError, OSError):
                continue

        self.assertEqual(
            len(deprecated_usages),
            0,
            f"Found deprecated construct usage: {deprecated_usages}",
        )

    def test_python_syntax_validity(self):
        """Verify all Python files have valid Python 3.12 syntax."""
        python_files = self.get_python_files()
        syntax_errors = []

        for filepath in python_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Try to parse the file
                try:
                    ast.parse(content, filename=str(filepath))
                except SyntaxError as e:
                    syntax_errors.append(f"{filepath}:{e.lineno}: {e.msg}")
            except (UnicodeDecodeError, OSError):
                continue

        self.assertEqual(len(syntax_errors), 0, f"Syntax errors found: {syntax_errors}")

    def test_string_formatting_compatibility(self):
        """Check for Python 2 style string formatting that might cause issues."""
        python_files = self.get_python_files()
        potential_issues = []

        for filepath in python_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Look for old-style string formatting patterns that might be problematic
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    # Skip comments
                    if line.strip().startswith("#"):
                        continue

                    # Check for potentially problematic patterns
                    if re.search(r"%[sd].*%.*\(", line):
                        potential_issues.append(
                            f"{filepath}:{i}: Possible old-style string formatting"
                        )
            except (UnicodeDecodeError, OSError):
                continue

        # This is informational - we don't fail the test for this
        if potential_issues:
            print(f"INFO: Found potential string formatting issues: {potential_issues}")

    def test_print_function_usage(self):
        """Verify print is used as a function, not statement."""
        python_files = self.get_python_files()
        print_issues = []

        for filepath in python_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse the AST to check for print statements
                try:
                    tree = ast.parse(content, filename=str(filepath))

                    # Walk the AST looking for Print nodes (Python 2 style)
                    for node in ast.walk(tree):
                        if hasattr(ast, "Print") and isinstance(node, ast.Print):
                            print_issues.append(
                                f"{filepath}:{node.lineno}: Print statement found"
                            )
                except SyntaxError:
                    # Already caught in syntax test
                    pass
            except (UnicodeDecodeError, OSError):
                continue

        self.assertEqual(
            len(print_issues),
            0,
            f"Found print statements (should be print functions): {print_issues}",
        )

    def test_encoding_declarations(self):
        """Check that files have proper encoding declarations if needed."""
        python_files = self.get_python_files()
        encoding_info = []

        for filepath in python_files:
            try:
                with open(filepath, "rb") as f:
                    first_line = f.readline()
                    second_line = f.readline()

                # Check if file contains non-ASCII characters
                try:
                    with open(filepath, "r", encoding="ascii") as f:
                        f.read()
                    # File is pure ASCII, no encoding declaration needed
                except UnicodeDecodeError:
                    # File contains non-ASCII characters
                    first_str = first_line.decode("utf-8", errors="ignore")
                    second_str = second_line.decode("utf-8", errors="ignore")

                    has_encoding = (
                        "coding" in first_str
                        or "coding" in second_str
                        or "encoding" in first_str
                        or "encoding" in second_str
                    )

                    if not has_encoding:
                        encoding_info.append(
                            f"{filepath}: Contains non-ASCII but no encoding declaration"
                        )
            except (UnicodeDecodeError, OSError):
                continue

        # This is informational - modern Python handles UTF-8 by default
        if encoding_info:
            print(
                f"INFO: Files with non-ASCII characters but no encoding declaration: {encoding_info}"
            )


class TestPackageStructure(unittest.TestCase):
    """Test that the package structure is correct for Python 3.12."""

    def test_setup_py_python_requires(self):
        """Verify setup.py specifies correct Python version requirement."""
        setup_py = Path(__file__).parent / "setup.py"

        if setup_py.exists():
            with open(setup_py, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for python_requires
            self.assertIn(
                "python_requires", content, "setup.py should specify python_requires"
            )

            # Check that it requires Python 3.8 or higher
            if "python_requires" in content:
                # Extract the python_requires value
                match = re.search(r"python_requires\s*=\s*['\"]([^'\"]+)['\"]", content)
                if match:
                    requirement = match.group(1)
                    self.assertTrue(
                        ">=3.8" in requirement
                        or ">=3.9" in requirement
                        or ">=3.10" in requirement,
                        f"python_requires should specify >=3.8, found: {requirement}",
                    )

    def test_package_imports(self):
        """Test that package imports work correctly."""
        # Test basic import structure
        sadi_dir = Path(__file__).parent / "sadi"

        if sadi_dir.exists():
            init_file = sadi_dir / "__init__.py"
            self.assertTrue(init_file.exists(), "sadi package should have __init__.py")

            # Try to parse the __init__.py file
            try:
                with open(init_file, "r", encoding="utf-8") as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                self.fail(f"Syntax error in sadi/__init__.py: {e}")


def run_compatibility_tests():
    """Run compatibility tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestPython312CompatibilityStandalone,
        TestPackageStructure,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    print("Running Python 3.12 compatibility tests...")
    print("=" * 60)

    result = run_compatibility_tests()

    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}")
            print(f"  {traceback}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}")
            print(f"  {traceback}")

    if result.wasSuccessful():
        print("\n✅ All Python 3.12 compatibility tests passed!")
    else:
        print("\n❌ Some tests failed.")

    sys.exit(0 if result.wasSuccessful() else 1)
