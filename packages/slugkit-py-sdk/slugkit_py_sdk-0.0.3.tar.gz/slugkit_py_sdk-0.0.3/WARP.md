# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

SlugKit Python SDK is a Python library for generating human-readable IDs using the SlugKit.dev service. The SDK provides both synchronous and asynchronous clients, along with a comprehensive CLI tool.

## Architecture

### Core Components

**Client Architecture**: The SDK follows a dual-client pattern:
- `SyncClient` - Synchronous HTTP client using httpx
- `AsyncClient` - Asynchronous HTTP client using httpx async
- Both clients share common base classes in `base.py` for generator functionality

**Generator Pattern**: Three main generator types implemented via composition:
- `SyncSlugGenerator`/`AsyncSlugGenerator` - Main ID generation with streaming support
- `RandomGenerator`/`AsyncRandomGenerator` - Pattern-based ID generation
- All generators support method chaining for configuration (`.with_limit()`, `.with_batch_size()`, etc.)

**API Endpoints**: The SDK abstracts several SlugKit API endpoints:
- `/gen/mint` - Generate new IDs (increments counter)
- `/gen/slice` - Generate IDs from specific sequence (dry-run, no counter increment)
- `/gen/forge` - Generate IDs from patterns
- `/gen/reset` - Reset project generator
- `/gen/stats/latest` - Get generator statistics

### Key Design Patterns

**Streaming Support**: Both clients support streaming large batches of IDs to handle high-volume generation efficiently without memory issues.

**Configuration Chaining**: Generators support fluent configuration:
```python
generator.with_limit(1000).with_batch_size(100).starting_from(500)
```

**Series/Project Support**: Generators can target specific series within a project using bracket notation:
```python
client["series-slug"]  # Returns generator for specific series
```

## Development Commands

### Building and Publishing

```bash
# Build the package
make build

# Publish to PyPI
make publish
```

### Package Management

This project uses `uv` as the package manager. Dependencies are managed in `pyproject.toml`:

```bash
# Install development dependencies
uv sync

# Run with uv
uv run python -m slugkit.cli --help
```

### Testing

This project uses pytest for comprehensive testing of both sync and async clients:

```bash
# Install test dependencies
make install-test-deps

# Run all tests
make test

# Run tests with verbose output
make test-verbose

# Run tests with coverage (requires pytest-cov)
make test-coverage

# Run specific test files
uv run --group test pytest tests/test_sync_client.py
uv run --group test pytest tests/test_async_client.py
uv run --group test pytest tests/test_cli.py
```

**Test Structure**:
- `tests/test_sync_client.py` - Comprehensive sync client tests including streaming, error handling, and edge cases
- `tests/test_async_client.py` - Async client tests with mocked functionality
- `tests/test_cli.py` - CLI command tests using Typer's test runner
- `tests/conftest.py` - Shared fixtures and test configuration

**Test Environment**: Tests use dedicated API keys and project (`whole-blond-rower-a597`) for safe testing without affecting production data.

### Testing the CLI

The CLI tool `slugkit` supports multiple commands:

```bash
# Generate IDs
slugkit mint 5
slugkit mint 10 --batch-size 2

# Test patterns
slugkit forge "your-pattern" --seed "test-seed" --count 5

# Slice IDs (dry-run from sequence)
slugkit slice 100 5

# Get stats and manage generator
slugkit stats
slugkit reset
```

### Environment Configuration

Required environment variables:
```bash
export SLUGKIT_BASE_URL="https://dev.slugkit.dev/api/v1"
export SLUGKIT_API_KEY="your-api-key"
```

## Code Organization

**Source Structure**:
- `src/slugkit/` - Main package code
- `src/slugkit/base.py` - Shared base classes and common functionality
- `src/slugkit/sync_client.py` - Synchronous client implementation
- `src/slugkit/async_client.py` - Asynchronous client implementation  
- `src/slugkit/cli.py` - Command-line interface using Typer
- `src/slugkit/__init__.py` - Package exports

**Example Scripts**:
- `martian-bots.py` - Demo script showing multi-series ID generation for creating test data

## Important Implementation Details

**Error Handling**: The SDK handles HTTP errors gracefully and provides meaningful error messages. 404 errors from the API are caught and re-raised with response text.

**Streaming Implementation**: The streaming generators use httpx's streaming response handling to process large ID batches line by line without loading everything into memory.

**Authentication**: All authenticated endpoints require an API key. The SDK validates API key presence for operations that require it and provides clear error messages when missing.

**Dry Run Mode**: The "slice" functionality allows generating IDs from specific sequences without incrementing the project counter, useful for testing and previews.
