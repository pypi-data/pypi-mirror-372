# Zia Image Recognition SDK

A simple, ergonomic Python SDK for the Zia Image Recognition API.

For more detailed information about the project architecture and design decisions, see [BUILD_SUMMARY.md](BUILD_SUMMARY.md).

## Features

- **Ergonomics first** - Single-line calls for common tasks
- **Type safety** - Rich typings with IDE autocompletion
- **Zero config by default** - Sensible defaults with environment variable support
- **Predictable errors** - Typed exceptions with actionable messages
- **Async/await support** - Modern Python async patterns
- **Image Recognition & Task Management** - Create tasks, upload images, and retrieve results
- **Catalog Management** - Create, update, and retrieve catalog items
- **Raw JSON Access** - Flexible data access for custom processing

## Installation

### Using Poetry (Recommended for Development)

[Poetry](https://python-poetry.org/) is a modern dependency management tool for Python.

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Clone and install the SDK
git clone https://github.com/neurolabs/zia-sdk-python.git
cd zia-sdk-python

# Install with all dependencies (including DataFrame utilities)
poetry install --with dev

# Or install specific extras
poetry install --extras "databricks" # For Databricks support (includes pandas and pyspark)
poetry install --extras "all"        # For all optional dependencies

# Activate the virtual environment
poetry shell
```

### Using pip (Production)

```bash
# Basic installation (no DataFrame support)
pip install zia-sdk-python

# With Databricks support (includes pandas and pyspark)
pip install zia-sdk-python[databricks]

# With all optional dependencies
pip install zia-sdk-python[all]

# Or install from GitHub
pip install git+https://github.com/neurolabs/zia-sdk-python.git
```

For detailed installation instructions, see [INSTALLATION.md](INSTALLATION.md).

## Quick Start

### Configuration

The SDK supports multiple ways to configure your API key:

#### 1. Environment Variables (Recommended)

```bash
export NEUROLABS_API_KEY="your-api-key-here"
```

#### 2. .env File

```bash
# Copy the example file
cp env.template .env

# Edit .env with your API key
NEUROLABS_API_KEY=your-api-key-here
```

#### 3. Command Line Arguments

```python
client = Zia(api_key="your-api-key-here")
```

### Async Usage (Recommended)

```python
import asyncio
from neurolabszia import Zia, NLCatalogItemCreate

async def main():
    # Initialize client (uses NEUROLABS_API_KEY env var)
    async with Zia() as client:
        # Health check
        is_healthy = await client.health_check()
        print(f"API Health: {is_healthy}")
        
        # List catalog items
        items = await client.catalog.list_items(limit=10)
        print(f"Found {len(items)} catalog items")
        
        # Create a catalog item
        new_item = NLCatalogItemCreate(
            name="My Product",
            brand="My Brand",
            barcode="1234567890123"
        )
        
        # Add thumbnail binary data if available
        # with open("thumbnail.jpg", "rb") as f:
        #     new_item.thumbnail = f.read()
        
        created_item = await client.catalog.create_item(new_item)
        print(f"Created: {created_item.name}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Sync Usage (Simple Operations)

```python
from neurolabszia import Zia

# Initialize client
client = Zia()

# Health check
is_healthy = client.health_check_sync()
print(f"API Health: {is_healthy}")

# List catalog items
items = client.list_items_sync(limit=10)
print(f"Found {len(items)} catalog items")

# List tasks
tasks = client.list_tasks_sync(limit=5)
print(f"Found {len(tasks)} tasks")
```

## Configuration

The SDK supports multiple configuration sources with the following precedence:

1. **Explicit parameters** - Passed to `Zia()` constructor
2. **Environment variables** - Set in your environment
3. **Config file** - Set multiple parameters using a config file 

### Environment Variables

```bash
export NEUROLABS_API_KEY="your-api-key"
export NEUROLABS_BASE_URL="https://api.neurolabs.ai/v2"  # Optional
export NEUROLABS_TIMEOUT="30.0"  # Optional
export NEUROLABS_MAX_RETRIES="3"  # Optional
```

### Explicit Configuration

```python
client = Zia(
    api_key="your-api-key",
    base_url="https://api.neurolabs.ai/v2",
    timeout=30.0,
    max_retries=3
)
```

## API Reference

### Client

The main `Zia` client provides access to all API functionality:

```python
client = Zia()

# Catalog operations
await client.catalog.list_items()
await client.catalog.create_item(item)
await client.catalog.get_item(uuid)

# Image recognition operations
await client.task_management.list_tasks()
await client.task_management.create_task(task)
await client.image_recognition.upload_images(task_uuid, image_paths)
```

### Catalog Operations

#### List Items

```python
items = await client.catalog.list_items(
    name="product name",  # Optional filter
    limit=50,            # Max 100
    offset=0             # Pagination
)
```

#### Create Item

```python
from neurolabszia import NLCatalogItemCreate

item = NLCatalogItemCreate(
    name="Product Name",
    brand="Brand Name",
    barcode="1234567890123",
    height=0.1,  # meters
    width=0.05,  # meters
    depth=0.02   # meters
)

# Add thumbnail binary data if available
with open("thumbnail.jpg", "rb") as f:
    item.thumbnail = f.read()

created_item = await client.catalog.create_item(item)
```

#### Upload Reference Images

```python
image_paths = [Path("image1.jpg"), Path("image2.jpg")]
updated_item = await client.catalog.upload_reference_images(
    item_uuid="item-uuid",
    image_paths=image_paths
)
```

### Image Recognition Operations

#### Create Task

```python
from neurolabszia import NLIRTaskCreate

task = NLIRTaskCreate(
    name="My Recognition Task",
    catalog_items=["item-uuid-1", "item-uuid-2"],
    compute_realogram=True,
    compute_shares=True
)

created_task = await client.task_management.create_task(task)
```

#### Upload Images

```python
# Upload local images
image_paths = [Path("image1.jpg"), Path("image2.jpg")]
result_uuids = await client.image_recognition.upload_images(
    task_uuid="task-uuid",
    image_paths=image_paths
)

# Upload image URLs
image_urls = [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
]
result_uuids = await client.image_recognition.upload_image_urls(
    task_uuid="task-uuid",
    image_urls=image_urls
)
```

#### Get Results

```python
# Get all results for a task
results = await client.result_management.get_task_results(
    task_uuid="task-uuid",
    limit=50,
    offset=0
)

# Get specific result
result = await client.result_management.get_result(
    task_uuid="task-uuid",
    result_uuid="result-uuid"
)
```

### Raw JSON Access

For flexible data processing, you can access raw JSON responses:

```python
# Get raw JSON without parsing
raw_result = await client.result_management.get_result_raw(
    task_uuid="task-uuid",
    result_uuid="result-uuid"
)

# Access data directly
print(f"Status: {raw_result['status']}")
print(f"Duration: {raw_result.get('duration')}")

# Flexible data processing
if 'coco' in raw_result and raw_result['coco']:
    annotations = raw_result['coco'].get('annotations', [])
    for annotation in annotations:
        score = annotation.get('neurolabs', {}).get('score', 0)
        if score > 0.9:
            print(f"High confidence: {score}")
```

### IRResults DataFrame Conversion

#### Spark Integration

```python
from neurolabszia.utils import to_spark_dataframe
from pyspark.sql import SparkSession

# Create Spark session
spark = SparkSession.builder.appName("ZiaAnalysis").getOrCreate()

# Convert to Spark DataFrame
spark_df = to_spark_dataframe(results, spark)
spark_df.show()

# Write to Delta table
spark_df.write.format("delta").mode("overwrite").saveAsTable("catalog.schema.table")

# Import the utilities

from dataframe import (
    ir_results_to_dataframe,
    ir_results_to_summary_dataframe,
    analyze_results_dataframe,
    filter_high_confidence_detections,
    get_product_summary,
)

# Get results

results = await client.result_management.get_all_task_results(task_uuid)

# Convert to detailed DataFrame (one row per detection)

df_detailed = ir_results_to_dataframe(results)
print(f"Found {len(df_detailed)} detections")

# Convert to summary DataFrame (one row per result)

df_summary = ir_results_to_summary_dataframe(results)
print(f"Processed {len(df_summary)} images")

```

## Error Handling

The SDK provides typed exceptions for different error scenarios:

```python
from neurolabszia import (
    NeurolabsError,
    NeurolabsAuthError,
    NeurolabsRateLimitError,
    NeurolabsValidationError
)

try:
    await client.catalog.create_item(item)
except NeurolabsAuthError as e:
    print(f"Authentication failed: {e}")
except NeurolabsRateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after} seconds")
except NeurolabsValidationError as e:
    print(f"Validation error: {e}")
except NeurolabsError as e:
    print(f"Unexpected error: {e}")
```

## Models

The SDK uses Pydantic models for type safety and validation:

### CatalogItem

```python
from neurolabszia import NLCatalogItem

item = NLCatalogItem(
    uuid="item-uuid",
    status="ONBOARDED",
    thumbnail_url="https://...",
    name="Product Name",
    brand="Brand Name",
    created_at=datetime.now(),
    updated_at=datetime.now()
)
```

### IRTask

```python
from neurolabszia import NLIRTask

task = NLIRTask(
    uuid="task-uuid",
    name="Task Name",
    created_at=datetime.now(),
    updated_at=datetime.now(),
    compute_realogram=False,
    compute_shares=False
)
```

### IRResult

```python
from neurolabszia import NLIRResult

result = NLIRResult(
    uuid="result-uuid",
    task_uuid="task-uuid",
    image_url="https://...",
    status="PROCESSED",
    failure_reason="",
    created_at=datetime.now(),
    updated_at=datetime.now(),
    confidence_score=0.95
)
```

## Development

### Setup

```bash
git clone <repository>
cd zia-sdk-python
poetry install
```

### Testing

```bash
# Run all tests 
# NOTE: Integration tests create actual items, tasks, image processing in the backend, based on your API KEY 
poetry run pytest

# Run with coverage
poetry run pytest --cov=zia --cov-report=html

# Run specific test file
poetry run pytest zia/tests/test_client.py -v
```

### Code Formatting

```bash
# Format code
poetry run black .
poetry run isort .

# Check formatting
poetry run black --check .
poetry run isort --check-only .
```

### Type Checking

```bash
poetry run mypy zia/
```

### Linting

```bash
poetry run ruff check .
```

## CLI Interface

The SDK includes a command-line interface:

```bash
# Health check
neurolabszia health

# List items
neurolabszia items 10

# List tasks
neurolabszia tasks 5
```

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
