# Pmini SDK Python

Python SDK for Pmini quadcopter with gRPC support and auto-generated wrapper classes.

## Features

- **MAVLink Integration**: Direct communication with Pmini quadcopter via MAVLink protocol
- **gRPC Support**: Modern gRPC API with auto-generated Python classes
- **Type Safety**: Full type hints and IDE support for all generated classes
- **MAVSDK-Style API**: Familiar API design with comprehensive documentation
- **Poetry Package Management**: Modern Python packaging and dependency management

## Quick Start

### Option 1: Development Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd pmini_sdk_python

# Setup development environment (installs Poetry if needed)
./setup_dev.sh

# Activate Poetry shell
poetry shell
```

### Option 2: Manual Setup

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Generate gRPC classes
./tools/run_grpc_protoc.sh
```

### Option 3: Package Installation

```bash
# Build the package
./build_package.sh

# Install the built package
pip install ./dist/pmini-*.whl
```

## Generated Classes

The SDK automatically generates type-safe Python classes from protobuf definitions:

### Basic Usage

```python
from pmini_sdk_python.generated import (
    TakeoffRequest, 
    Position, 
    DroneService,
    CommandResponse
)

# Create requests with type safety
takeoff_request = TakeoffRequest(altitude=10.0)
position = Position(x=1.0, y=2.0, z=3.0)

# Use with gRPC service
import grpc
channel = grpc.insecure_channel('localhost:50051')
drone_service = DroneService(channel)

response = drone_service.takeoff(takeoff_request)
print(f"Takeoff success: {response.success}")
```

### Available Classes

- **Request Classes**: `TakeoffRequest`, `LandRequest`, `ArmRequest`, `DisarmRequest`, `SetModeRequest`
- **Response Classes**: `CommandResponse`, `StatusResponse`, `PositionResponse`
- **Data Classes**: `TelemetryData`, `Position`, `Velocity`, `Attitude`
- **Service Classes**: `DroneService` (gRPC service wrapper)

### Class Features

- **Type Safety**: All fields have proper type hints
- **Documentation**: MAVSDK-style docstrings with parameter descriptions
- **Constructors**: Explicit constructors with parameter validation
- **Conversion Methods**: `to_proto()` and `from_proto()` for gRPC interop

## Examples

### MAVLink Examples

```bash
cd examples
python3 takeoff.py  # MAVLink-based takeoff example
```

### gRPC Examples

```bash
cd examples
python3 generated_classes_example.py      # Generated classes usage
python3 constructor_examples.py           # Constructor demonstrations
python3 improved_documentation_example.py # Documentation examples
```

## Development

### Regenerating Classes

When you modify `proto/drone.proto`, regenerate the wrapper classes:

```bash
./tools/run_grpc_protoc.sh
```

### Building the Package

```bash
./build_package.sh
```

### Project Structure

```
pmini_sdk_python/
├── proto/                    # Protocol buffer definitions
│   └── drone.proto
├── pmini_sdk_python/         # Main package
│   ├── generated/            # Auto-generated gRPC classes
│   ├── mavlink_client.py     # MAVLink implementation
│   └── pmini.py             # Main SDK class
├── tools/                    # Code generation tools
│   ├── templates/            # Jinja2 templates for class generation
│   ├── generate_classes.py   # Class generator script
│   └── run_grpc_protoc.sh   # Build script
├── examples/                 # Usage examples
├── test/                    # Integration tests
└── docs/                    # Documentation
```

### Dependencies

- **Runtime**: `grpcio`, `pymavlink`, `plotly`, `dash`
- **Development**: `grpcio-tools`, `jinja2`, `poetry`
- **Testing**: `pytest`, `pytest-cov`

# Integration Tests for Pmini SDK

This directory contains integration tests for the Pmini SDK Python library.

## Test Structure

- `conftest.py` - Pytest configuration and fixtures
- `test_basic.py` - Basic tests that don't require simulation
- `test_connection.py` - Connection tests that require simulation
- `run_integration_tests.py` - Test runner script

## Prerequisites

1. Install dependencies:

```bash
pip install pytest pytest-cov
```

2. Install the SDK:
```bash
pip install -e .
```

## Running Tests

### Note 

For the integration testing, autopilot simulation is required.
You can use this repository to start the simulation: https://gitlab.com/regislab/pathfindermini/pf_mini_gazebo

```bash
git clone git@gitlab.com:regislab/pathfindermini/pf_mini_gazebo.git && cd pf_mini_gazebo
```

Launch the simulation with the following command

```bash
make run
```

### Basic Tests (No Simulation Required)
```bash
# Run basic tests only
python -m pytest test/test_basic.py -v

# Or use the test runner
python test/run_integration_tests.py --test-path test/test_basic.py
```

### Connection Tests (Requires Simulation)
```bash
# Start your simulation container first, then:
python -m pytest test/test_connection.py -v

```

### All Tests
```bash
# Run all tests
python -m pytest test/ -v
```

### With Markers
```bash
# Run only integration tests
python -m pytest test/ -m integration

# Run only connection tests
python -m pytest test/ -m connection

# Exclude slow tests
python -m pytest test/ -m "not slow"
```

## Test Configuration

The tests are configured to connect to a simulation running on:
- Host: `192.168.4.1`
- Port: `8080`
- Protocol: `UDP`

You can modify the connection settings in `conftest.py` if your simulation uses different parameters.

## Test Categories

### Basic Tests (`test_basic.py`)
- SDK import verification
- Configuration object creation
- Enum availability
- Logging setup

### Connection Tests (`test_connection.py`)
- Connection establishment
- Connection stability
- MAVLink client functionality
- Optical flow data availability
- Connection timeout handling
- Connection recovery

## Adding New Tests

1. Create a new test file: `test_<feature>.py`
2. Use the existing fixtures from `conftest.py`
3. Add appropriate markers to your tests
4. Follow the existing test patterns

Example:
```python
import pytest
import logging

class TestNewFeature:
    @pytest.mark.integration
    def test_new_feature(self, pmini_instance, wait_for_connection):
        logger = logging.getLogger(__name__)
        logger.info("Testing new feature")
        
        # Your test logic here
        assert True
        logger.info("✅ New feature test passed")
```

## Troubleshooting

### Connection Timeout
If tests fail with connection timeout:
1. Ensure your simulation container is running
2. Check that the simulation is listening on the correct port
3. Verify network connectivity between test environment and simulation

### Import Errors
If you get import errors:
1. Make sure the SDK is installed: `pip install -e .`
2. Check that all dependencies are installed: `pip install -r requirements.txt`

### Test Failures
- Check the logs for detailed error messages
- Use `-v` flag for verbose output
- Use `-s` flag to see print statements 
