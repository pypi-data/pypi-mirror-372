# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Vidur is a high-fidelity and extensible LLM inference simulator for capacity planning, testing research ideas, and studying system performance without requiring GPU access (except for initial profiling). It combines Python simulation logic with C++ performance-critical components.

## Architecture

- **Hybrid C++/Python codebase**: Performance-critical components in C++ (`csrc/`) with Python bindings, high-level simulation logic in Python (`vidur/`)
- **Event-driven simulation**: Core simulator uses discrete event simulation with priority queue for scheduling
- **Plugin architecture**: Extensible schedulers, request generators, and execution time predictors via registry pattern
- **Metrics collection**: Comprehensive metrics with optional Chrome tracing and W&B integration

### Key Components

- `vidur/simulator.py`: Main event-driven simulation engine
- `vidur/entities/`: Core simulation entities (clusters, replicas, batches, requests)
- `vidur/scheduler/`: Pluggable scheduling algorithms (global, replica, stage-level)
- `vidur/request_generator/`: Workload generation from traces or synthetic patterns
- `vidur/execution_time_predictor/`: Performance prediction models
- `vidur/config/`: Configuration system with CLI argument parsing
- `csrc/`: C++ implementations for performance-critical operations

## Development Commands

### Building
```bash
# Install in development mode (builds C++ extensions)
pip install -e .

# Build C++ native extensions only
make build/native

# Build wheel package
make build/wheel
```

### Code Quality
```bash
# Format all code (Python + C++)
make format

# Lint all code
make lint

# Individual formatters
make format/black    # Python with black
make format/isort    # Python imports
make format/clang-format  # C++ code

# Individual linters
make lint/black      # Check Python formatting
make lint/isort      # Check import ordering
make lint/flake8     # Python style
make lint/clang-tidy # C++ static analysis
make lint/clang-format # Check C++ formatting
```

### Running Simulation
```bash
# Basic simulation run
python -m vidur.main

# Show all CLI arguments
python -m vidur.main --help

# Run all working tests
make test
```

## Configuration System

The codebase uses a dataclass-based configuration system with CLI argument generation. Configurations are hierarchical and type-safe, supporting different schedulers, request generators, and hardware SKUs through polymorphic config classes.

## Native C++ Integration

Performance-critical paths use C++ implementations via pybind11:
- Batch processing and execution time prediction
- Configuration objects for performance-sensitive operations
- Must build native extensions before running simulations

## Supported Models and Hardware

Currently supports Llama-3 (8B, 70B) on A100/H100 DGX and multi-GPU nodes with various tensor/pipeline parallelism configurations. Adding new models requires profiling on target hardware.

## Documentation Guidelines

- Documentation should be to-the-point and concise
- Update documentation as needed when code changes
- Maintain technical accuracy without unnecessary verbosity