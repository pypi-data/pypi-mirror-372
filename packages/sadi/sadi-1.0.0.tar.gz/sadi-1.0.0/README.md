# SADI Python

[![Python CI](https://github.com/jpmccu/sadi/actions/workflows/python-ci.yml/badge.svg)](https://github.com/jpmccu/sadi/actions/workflows/python-ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: BSD](https://img.shields.io/badge/License-BSD-yellow.svg)](https://opensource.org/licenses/BSD-3-Clause)

SADI (Semantic Automated Discovery and Integration) is a framework for creating semantic web services that consume and produce RDF data. This is the Python implementation of SADI.

## Features

- 🐍 **Python 3.8-3.12 Support**: Fully compatible with modern Python versions
- 🔧 **Easy Service Creation**: Simple decorators and classes for creating SADI services
- 📊 **RDF Processing**: Built-in support for RDF data serialization and deserialization
- 🌐 **Multiple Formats**: Support for Turtle, RDF/XML, JSON-LD, and RDFa
- ⚡ **Asynchronous Support**: Built-in support for async service operations
- 🧪 **Comprehensive Testing**: Full test suite covering all SADI functionality

## Installation

### From PyPI (recommended)

```bash
pip install sadi
```

### From Source

```bash
git clone https://github.com/jpmccu/sadi.git
cd sadi/python/sadi.python
pip install -e .
```

## Quick Start

### Creating a Simple SADI Service

```python
from sadi import sadi

@sadi.service(
    name="ExampleService",
    description="An example SADI service",
    inputClass="http://example.org/Input",
    outputClass="http://example.org/Output"
)
def example_service(input_graph, output_graph):
    # Process RDF data
    for subject in input_graph.subjects():
        output_graph.add((subject, URIRef("http://example.org/processed"), Literal("true")))
    return output_graph

if __name__ == '__main__':
    sadi.run(example_service)
```

### Using SADI Client

```python
from sadi.client import SADIClient

client = SADIClient()
result = client.call_service("http://example.org/service", input_data)
```

## Testing

This package includes a comprehensive test suite covering all SADI functionality:

```bash
# Run all tests
python run_tests.py

# Run compatibility tests only (no dependencies required)
python test_compatibility.py

# Run with make (if available)
make test
```

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/jpmccu/sadi.git
cd sadi/python/sadi.python

# Install in development mode
pip install -e .[dev]

# Run tests
make test

# Format code
make format

# Check code quality
make lint
```

### Available Make Commands

- `make install` - Install package
- `make install-dev` - Install with development dependencies
- `make test` - Run all tests
- `make lint` - Run code linting
- `make format` - Format code with black and isort
- `make build` - Build package distributions
- `make clean` - Clean build artifacts

## Python 3.12 Compatibility

This package has been updated for full Python 3.12 compatibility. Key changes include:

- ✅ Removed deprecated `buffer()` function calls
- ✅ Eliminated Python 2/3 compatibility libraries
- ✅ Updated `basestring` usage to `str`
- ✅ Comprehensive test coverage for compatibility

See [PYTHON312_COMPATIBILITY.md](PYTHON312_COMPATIBILITY.md) for detailed information.

## Testing Documentation

For comprehensive testing information, see [TESTING.md](TESTING.md).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests as needed
5. Run the test suite: `make test`
6. Submit a pull request

## License

This project is licensed under the BSD 3-Clause License - see the LICENSE file for details.

## Support

- **Python Versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Documentation**: [SADI Documentation](http://code.google.com/p/sadi/)
- **Issues**: [GitHub Issues](https://github.com/jpmccu/sadi/issues)

## Links

- [SADI Homepage](http://code.google.com/p/sadi/)
- [GitHub Repository](https://github.com/jpmccu/sadi)
- [Python Package Index](https://pypi.org/project/sadi/)