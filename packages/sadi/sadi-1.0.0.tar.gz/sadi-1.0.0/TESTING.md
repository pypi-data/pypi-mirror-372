# SADI Python Testing Guide

This document describes the comprehensive test suite for the SADI Python framework and how to run the tests.

## Test Structure

The SADI Python project now includes several test suites:

### 1. Python 3.12 Compatibility Tests (`test_compatibility.py`)
**No dependencies required** - Tests core Python 3.12 compatibility:
- Verifies no deprecated `buffer()` function calls
- Ensures Python 2/3 compatibility imports have been removed
- Checks that `basestring` has been replaced with `str`
- Validates Python syntax for all source files
- Verifies package structure and metadata

### 2. Comprehensive SADI Tests (`test_sadi_comprehensive.py`)
**Requires dependencies** - Full test suite covering:
- Core SADI service functionality (service descriptions, invocation, HTTP methods)
- Data serialization/deserialization (RDF formats, JSON-LD, RDFa, Unicode handling)
- FRIR module (graph digests, canonicalization, hash generation)
- Individual and OntClass functionality
- Asynchronous service support
- HTTP client functionality
- Encoding and bytes handling in Python 3.12

### 3. Original Tests (`tests.py`)
**Requires dependencies** - The original test suite that includes:
- Basic service functionality tests
- Content negotiation tests
- RDF parsing and serialization tests
- FRIR identifier tests
- Unicode handling tests

## Running Tests

### Quick Test (No Dependencies Required)
To run just the compatibility tests without installing dependencies:

```bash
cd python/sadi.python
python test_compatibility.py
```

### Complete Test Suite
To run all tests, first install dependencies:

```bash
cd python/sadi.python
pip install -e .
```

Then run all tests:

```bash
python run_tests.py
```

### Individual Test Suites

Run compatibility tests only:
```bash
python test_compatibility.py
```

Run comprehensive tests (requires dependencies):
```bash
python test_sadi_comprehensive.py
```

Run original tests (requires dependencies):
```bash
python tests.py
```

## Test Runner Features

The `run_tests.py` script automatically:
- Checks for available dependencies
- Runs compatibility tests (always)
- Runs comprehensive tests (if dependencies available)
- Runs original tests (if dependencies available)
- Provides clear success/failure reporting
- Suggests installation commands for missing dependencies

## Dependencies

Required for full testing:
- `rdflib>=4.0` - RDF library for Python
- `Werkzeug` - WSGI toolkit
- `webob` - WebOb request/response objects
- `python-dateutil` - Date/time parsing
- `pytidylib` - HTML tidy library

Install all dependencies:
```bash
pip install rdflib werkzeug webob python-dateutil pytidylib
```

## Python 3.12 Compatibility

The test suite specifically verifies Python 3.12 compatibility by ensuring:

1. **No `buffer()` function calls**: The deprecated `buffer()` function has been removed
2. **No future library imports**: Python 2/3 compatibility libraries are no longer needed
3. **No `basestring` usage**: Replaced with `str` in Python 3
4. **Valid syntax**: All files compile correctly with Python 3.12
5. **Proper encoding handling**: String vs bytes handling works correctly

## Test Coverage

The comprehensive test suite covers:

### SADI Service Functionality
- Service description generation (RDF/Turtle/JSON)
- Service invocation with different input/output formats
- HTTP method handling (GET for description, POST for invocation)
- Content negotiation (Accept headers)
- Error handling (405 for unsupported methods)

### Data Handling
- RDF parsing and serialization in multiple formats
- JSON-LD serialization/deserialization
- RDFa parsing and serialization
- Unicode character handling
- Multipart content parsing

### FRIR Module
- RDF graph digest generation
- Graph canonicalization and comparison
- Hash generation for RDF graphs
- Blank node handling

### Asynchronous Services
- Async service execution
- Status polling (202 responses)
- Result retrieval

## Running Tests in Different Environments

### Development Environment
```bash
# Install in development mode
pip install -e .

# Run all tests
python run_tests.py
```

### CI/CD Pipeline
```bash
# Install dependencies
pip install rdflib werkzeug webob python-dateutil pytidylib

# Run tests with verbose output
python test_compatibility.py -v
python test_sadi_comprehensive.py -v
```

### Docker Container
```bash
# In Dockerfile
RUN pip install rdflib werkzeug webob python-dateutil pytidylib
RUN cd /app/python/sadi.python && python run_tests.py
```

## Troubleshooting

### Common Issues

1. **Import errors**: Install missing dependencies with `pip install -e .`
2. **Syntax warnings**: These are from external dependencies (nose) and can be ignored
3. **Unicode errors**: Ensure your terminal supports UTF-8 encoding

### Debug Mode
Run individual tests with verbose output:
```bash
python -m unittest test_sadi_comprehensive.TestSADIService.test_service_invocation -v
```

## Contributing Tests

When adding new functionality to SADI Python:

1. Add compatibility tests to `test_compatibility.py` if introducing new Python 3.12 features
2. Add comprehensive tests to `test_sadi_comprehensive.py` for new functionality
3. Ensure all tests pass with `python run_tests.py`
4. Update this README if adding new test categories

### Test Naming Convention
- Test classes: `TestFunctionalityName`
- Test methods: `test_specific_behavior`
- Use descriptive docstrings for all tests

### Mock Usage
Use `unittest.mock` for external dependencies:
```python
@patch('urllib.request.urlopen')
def test_external_api(self, mock_urlopen):
    # Test implementation
```

## Performance

The test suite is designed to run quickly:
- Compatibility tests: ~1 second (no dependencies)
- Comprehensive tests: ~30-60 seconds (with dependencies)
- Original tests: ~30-60 seconds (with dependencies)

For faster development cycles, run just the compatibility tests during development and the full suite before committing.