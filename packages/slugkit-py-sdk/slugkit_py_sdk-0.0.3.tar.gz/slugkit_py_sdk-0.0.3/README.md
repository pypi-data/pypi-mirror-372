# SlugKit Python SDK

A Python SDK for generating human-readable IDs using SlugKit.dev service.

Please see [SlugKit documentation](https://dev.slugkit.dev) for information
on creating series and obtaining API keys.

## Installation

```bash
pip install slugkit-py-sdk
```

## API Overview

The SDK provides a comprehensive interface to generate human-readable IDs, test patterns, and manage generator state.

### Basic Usage

```python
from slugkit import SyncClient

# Initialize the client
client = SyncClient(
    base_url="https://dev.slugkit.dev/api/v1",
    api_key="your-api-key"
)

# Generate a single ID
id = client.mint()[0]

# Generate multiple IDs
ids = client.mint(count=5)

# Get generator stats
stats = client.mint.stats()

# Get series information
series_info = client.mint.series_info()

# Reset the generator
client.mint.reset()
```

### Advanced Generator Configuration

```python
# Configure generator with limits and batch sizes
generator = client.mint.with_limit(100).with_batch_size(10)

# Start from a specific sequence
generator = generator.starting_from(1000)

# Use dry-run mode (for testing)
generator = generator.with_dry_run()

# Generate IDs with configuration
ids = list(generator)
```

### Pattern Testing (Forge)

```python
# Test a pattern with various options
ids = client.forge(
    pattern="{adjective}-{noun}-{number:3d}",
    seed="optional-seed",
    sequence=1,
    count=5
)

# Use different pattern types
ids = client.forge(
    pattern="simple-{noun}-{number:2,hex}",
    count=3
)
```

### Series Management

```python
# Access a specific series
series_generator = client["series-slug"]

# Generate IDs for specific series
ids = series_generator(count=10)

# Get stats for specific series
stats = series_generator.stats()

# Get series info for specific series
series_info = series_generator.series_info()
```

### Async Usage

The SDK also provides an async client for use with async/await code:

```python
import asyncio
from slugkit import AsyncClient

async def main():
    # Initialize the async client
    client = AsyncClient(
        base_url="https://dev.slugkit.dev/api/v1",
        api_key="your-api-key"
    )

    # Generate a single ID
    id = await client.mint()[0]

    # Generate multiple IDs
    ids = await client.mint(count=5)

    # Get generator stats
    stats = await client.mint.stats()

    # Get series information
    series_info = await client.mint.series_info()

    # Reset the generator
    await client.mint.reset()

    # Test a pattern
    ids = await client.forge(
        pattern="{adjective}-{noun}-{number:3d}",
        seed="optional-seed",
        sequence=1,
        count=5
    )

    # Stream IDs asynchronously
    async for id in client.mint:
        print(id)

# Run the async code
asyncio.run(main())
```

## Command Line Interface

The SDK includes a command-line interface for easy usage:

### Generate IDs

```bash
# Generate a single ID
slugkit mint

# Generate multiple IDs
slugkit mint 5

# Generate IDs with custom batch size
slugkit mint 10 --batch-size 2
```

### Test Patterns

```bash
# Test a pattern
slugkit forge "your-pattern"

# Test with specific seed and sequence
slugkit forge "your-pattern" --seed "my-seed" --sequence 1

# Generate multiple test IDs
slugkit forge "your-pattern" --count 5
```

### Generator Management

```bash
# Get generator stats
slugkit stats

# Get series information
slugkit series-info

# Reset the generator
slugkit reset
```

### Configuration

The CLI can be configured using environment variables or command-line options:

```bash
# Set base URL
export SLUGKIT_BASE_URL="https://dev.slugkit.dev/api/v1"

# Set API key
export SLUGKIT_API_KEY="your-api-key"

# Or use command-line options
slugkit --base-url "https://dev.slugkit.dev/api/v1" --api-key "your-api-key" mint
```

### Output Format

The CLI supports different output formats:

```bash
# Text output (default)
slugkit mint

# JSON output
slugkit mint --output-format json
```

## Data Types

The SDK provides structured data types for API responses:

### StatsItem

Represents generator statistics:

```python
from slugkit.base import StatsItem

stats = client.mint.stats()
for item in stats:
    print(f"Event: {item.event_type}")
    print(f"Total Count: {item.total_count}")
    print(f"Request Count: {item.request_count}")
    print(f"Average Duration: {item.avg_duration_us}μs")
```

### SeriesInfo

Represents series information:

```python
from slugkit.base import SeriesInfo

series_info = client.mint.series_info()
print(f"Pattern: {series_info.pattern}")
print(f"Capacity: {series_info.capacity}")
print(f"Generated: {series_info.generated_count}")
print(f"Last Modified: {series_info.mtime}")
```

## API Response Examples

### Stats Response

```json
[
  {
    "event_type": "mint",
    "date_part": "total",
    "total_count": 104517,
    "request_count": 118,
    "total_duration_us": 1092348,
    "avg_duration_us": 10.45
  },
  {
    "event_type": "forge",
    "date_part": "total",
    "total_count": 15,
    "request_count": 5,
    "total_duration_us": 500,
    "avg_duration_us": 50.0
  }
]
```

### Series Info Response

```json
{
  "slug": "whole-blond-rower-a597",
  "org_slug": "alias-first-glute-67d9",
  "pattern": "{adverb}-{adjective}-{noun}-{number:3d}",
  "max_pattern_length": 80,
  "capacity": "1281739952493000",
  "generated_count": "105",
  "mtime": "2025-08-29T00:54:35.128902+00:00"
}
```

## Error Handling

The SDK provides comprehensive error handling:

```python
import httpx

try:
    ids = client.mint(count=10)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 400:
        print(f"Bad request: {e.response.text}")
    elif e.response.status_code == 401:
        print("Unauthorized - check your API key")
    elif e.response.status_code == 404:
        print("Resource not found")
    else:
        print(f"HTTP error {e.response.status_code}: {e.response.text}")
except httpx.ConnectError:
    print("Connection failed - check your network and base URL")
```

## Pattern Language

The SDK supports SlugKit's pattern language for generating structured IDs:

### Basic Tokens

- `{adjective}` - Random adjective
- `{noun}` - Random noun  
- `{adverb}` - Random adverb
- `{verb}` - Random verb
- `{color}` - Random color
- `{animal}` - Random animal

### Number Generators

- `{number:3d}` - 3-digit decimal number
- `{number:4,hex}` - 4-character hexadecimal
- `{number:2,oct}` - 2-character octal
- `{number:6,bin}` - 6-character binary

### Examples

```python
# Simple patterns
pattern1 = "{adjective}-{noun}"
pattern2 = "{color}-{animal}-{number:3d}"

# Complex patterns with constraints
pattern3 = "{adverb}-{adjective}-{noun}-{number:4,hex}[==5]"

# Generate IDs
ids = client.forge(pattern=pattern3, count=5)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
