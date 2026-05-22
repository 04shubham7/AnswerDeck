# Batch Processing API Documentation

## Overview

The AnswerDeck RAG system includes a powerful batch processing framework for parallel document indexing and embedding generation. This system provides:

- **Parallel Processing**: Process multiple documents concurrently using ThreadPoolExecutor or asyncio
- **Configurable Concurrency**: Control batch sizes and worker counts
- **Automatic Retry Logic**: Failed items are automatically retried with configurable delays
- **Progress Tracking**: Real-time progress monitoring and metrics
- **Error Handling**: Graceful error handling with detailed error reporting
- **Cancellation Support**: Cancel ongoing batch processing operations

## Quick Start

### Basic Usage

```python
from batch_processor import BatchProcessor, BatchProcessingConfig

# Create configuration
config = BatchProcessingConfig(
    batch_size=10,
    max_workers=4,
    max_retries=3,
    retry_delay=1.0,
    verbose=True,
)

# Initialize processor
processor = BatchProcessor(config)

# Define your processing function
def process_item(item):
    # Your processing logic here
    return processed_item

# Process items
items = [("item-1", data1), ("item-2", data2), ...]
progress = processor.process_items(items, process_item)

# Check results
print(f"Success: {progress.successful_items}/{progress.total_items}")
print(f"Success Rate: {processor.success_rate:.1f}%")
```

### With Progress Callback

```python
def on_progress(progress):
    """Called after each item is processed"""
    print(f"Progress: {progress.processed_items}/{progress.total_items}")
    print(f"Success Rate: {progress.success_rate:.1f}%")

progress = processor.process_items(
    items,
    process_item,
    on_progress=on_progress,
)
```

### Asynchronous Processing

```python
import asyncio

async def async_process_item(item):
    # Your async processing logic
    return await some_async_operation(item)

# Run async processing
progress = await processor.process_items_async(
    items,
    async_process_item,
)
```

## Configuration

### BatchProcessingConfig

The `BatchProcessingConfig` class controls batch processing behavior:

```python
@dataclass
class BatchProcessingConfig:
    batch_size: int = 10           # Items per batch
    max_workers: int = 4           # Concurrent workers
    max_retries: int = 3           # Retry attempts for failed items
    retry_delay: float = 1.0       # Delay between retries (seconds)
    timeout_per_item: float = 300.0  # Timeout per item (seconds)
    verbose: bool = False          # Detailed logging
```

### Example Configurations

**For Document Indexing with Rate Limiting:**
```python
config = BatchProcessingConfig(
    batch_size=10,
    max_workers=2,           # Lower concurrency to respect API limits
    max_retries=3,
    retry_delay=60.0,        # Wait 60 seconds between retries
    verbose=True,
)
```

**For CPU-Bound Tasks:**
```python
config = BatchProcessingConfig(
    batch_size=50,
    max_workers=8,           # More workers for CPU tasks
    max_retries=1,
    retry_delay=0.5,
    verbose=False,
)
```

**For I/O-Bound Tasks:**
```python
config = BatchProcessingConfig(
    batch_size=100,
    max_workers=20,          # Many workers for I/O tasks
    max_retries=3,
    retry_delay=2.0,
    verbose=False,
)
```

## API Reference

### BatchProcessor

Main class for managing batch processing operations.

#### Methods

##### `process_items(items, process_func, on_progress=None) -> ProcessingProgress`

Process a list of items synchronously using ThreadPoolExecutor.

**Parameters:**
- `items` (List[Tuple[str, T]]): List of (item_id, item_data) tuples
- `process_func` (Callable[[T], R]): Function to process each item
- `on_progress` (Optional[Callable]): Callback function for progress updates

**Returns:**
- `ProcessingProgress`: Final progress information

**Example:**
```python
items = [("doc-1", doc1), ("doc-2", doc2), ...]
progress = processor.process_items(items, process_func)
print(f"Processed {progress.successful_items} items successfully")
```

##### `process_items_async(items, process_func, on_progress=None) -> ProcessingProgress`

Process a list of items asynchronously using asyncio.

**Parameters:**
- `items` (List[Tuple[str, T]]): List of (item_id, item_data) tuples
- `process_func` (Callable[[T], Awaitable[R]]): Async function to process each item
- `on_progress` (Optional[Callable]): Callback function for progress updates

**Returns:**
- `ProcessingProgress`: Final progress information

**Example:**
```python
async def async_process(item):
    result = await get_embeddings(item)
    return result

progress = await processor.process_items_async(items, async_process)
```

##### `cancel() -> None`

Cancel ongoing batch processing.

**Example:**
```python
processor.cancel()
```

#### Properties

##### `is_processing -> bool`

Check if batch processing is currently active.

```python
if processor.is_processing:
    print("Processing is running")
```

##### `success_rate -> float`

Get the success rate as a percentage (0-100).

```python
rate = processor.success_rate
print(f"Success rate: {rate:.1f}%")
```

## Progress Tracking

### ProcessingProgress

Provides real-time progress information and metrics.

```python
@dataclass
class ProcessingProgress:
    status: ProcessingStatus          # Current status
    total_items: int                  # Total items
    processed_items: int              # Items processed
    successful_items: int             # Successful items
    failed_items: int                 # Failed items
    retry_items: int                  # Items being retried
    error_messages: List[str]         # Error details
    start_time: Optional[datetime]    # Start time
    elapsed_time: float               # Elapsed seconds
    estimated_remaining_time: float   # ETA in seconds
    progress_percentage: float        # 0-100%
```

### ProcessingStatus Enum

- `PENDING`: Waiting to start
- `IN_PROGRESS`: Currently processing
- `COMPLETED`: Finished successfully
- `FAILED`: Processing failed
- `CANCELLED`: User cancelled

### Progress Methods

```python
# Update timing information
progress.update_elapsed_time()

# Update progress percentage
progress.update_progress_percentage()

# Log a summary
progress.log_summary()
```

## Error Handling

### ItemProcessingResult

Result information for each processed item.

```python
@dataclass
class ItemProcessingResult:
    item_id: str              # Item identifier
    success: bool             # Processing successful?
    result: Optional[Any]     # Processing result
    error: Optional[str]      # Error message if failed
    retry_count: int          # Number of retries
    processing_time: float    # Time in seconds
```

### Handling Errors

```python
progress = processor.process_items(items, process_func)

if progress.failed_items > 0:
    print(f"Failed items: {progress.failed_items}")
    for error in progress.error_messages:
        print(f"  - {error}")
```

### Automatic Retry Logic

Failed items are automatically retried according to configuration:

```python
config = BatchProcessingConfig(
    max_retries=3,           # 3 retry attempts
    retry_delay=1.0,         # 1 second between retries
)

# If item fails initially, it will be retried up to 3 times
# with 1 second delay between attempts
```

## Use Cases

### Document Indexing with Rate Limiting

```python
from batch_processor import BatchProcessor, BatchProcessingConfig

config = BatchProcessingConfig(
    batch_size=10,
    max_workers=2,
    max_retries=3,
    retry_delay=60.0,  # Respect API rate limits
    verbose=True,
)

processor = BatchProcessor(config)

def embed_document(doc):
    return embeddings_model.embed(doc)

items = [(f"doc-{i}", doc) for i, doc in enumerate(documents)]
progress = processor.process_items(items, embed_document)
```

### Parallel Image Processing

```python
config = BatchProcessingConfig(
    batch_size=50,
    max_workers=8,
    max_retries=2,
    verbose=False,
)

processor = BatchProcessor(config)

def process_image(image_path):
    return transform_and_save_image(image_path)

image_paths = [Path(p) for p in glob("images/*.jpg")]
items = [(p.name, p) for p in image_paths]
progress = processor.process_items(items, process_image)
```

### Async API Calls

```python
import asyncio

config = BatchProcessingConfig(
    batch_size=100,
    max_workers=20,
    max_retries=3,
    timeout_per_item=30.0,
)

processor = BatchProcessor(config)

async def call_api(endpoint):
    return await http_client.get(endpoint)

items = [(f"endpoint-{i}", endpoint) for i, endpoint in enumerate(endpoints)]
progress = await processor.process_items_async(items, call_api)
```

## Performance Tuning

### Batch Size

- **Smaller batches (5-10)**: Better for APIs with rate limits
- **Larger batches (50-100)**: Better for local processing

### Worker Count

- **CPU-bound tasks**: Set to CPU count (typically 4-8)
- **I/O-bound tasks**: Set to 2-3x CPU count
- **Network requests**: Can be much higher (20-100)

### Timeout Configuration

```python
# For quick operations
config = BatchProcessingConfig(timeout_per_item=10.0)

# For long-running operations
config = BatchProcessingConfig(timeout_per_item=600.0)  # 10 minutes
```

### Retry Strategy

```python
# For critical operations
config = BatchProcessingConfig(
    max_retries=5,
    retry_delay=2.0,  # Exponential backoff would be better
)

# For non-critical operations
config = BatchProcessingConfig(
    max_retries=1,
    retry_delay=0.5,
)
```

## Logging

Enable detailed logging:

```python
import logging

logging.basicConfig(level=logging.INFO)

config = BatchProcessingConfig(verbose=True)
processor = BatchProcessor(config)
```

This will output:
- Processing start/end messages
- Per-item processing results
- Progress summaries
- Error details

## Integration with AnswerDeck RAG

### Updated indexing.py

The batch processor is integrated into the indexing pipeline:

```python
# See indexing_with_batch.py for full example
processor = BatchProcessor(config)
progress = processor.process_items(
    items,
    process_document_batch,
    on_progress=progress_callback,
)
```

## Best Practices

1. **Choose appropriate batch size** based on API limits and memory constraints
2. **Set reasonable timeouts** for your specific use case
3. **Monitor progress** using callbacks for large jobs
4. **Handle errors gracefully** by checking `progress.failed_items`
5. **Use retry delays** that respect service rate limits
6. **Log details** with `verbose=True` during development
7. **Test with small datasets** first before scaling up

## Troubleshooting

### Too Many Failures

```python
# Increase retry attempts and delay
config = BatchProcessingConfig(
    max_retries=5,
    retry_delay=5.0,
)
```

### Rate Limit Errors

```python
# Reduce concurrency and increase delays
config = BatchProcessingConfig(
    max_workers=1,      # Sequential processing
    batch_size=5,
    retry_delay=60.0,   # 60 seconds between batches
)
```

### Memory Issues

```python
# Process smaller batches
config = BatchProcessingConfig(
    batch_size=5,       # Smaller chunks
    max_workers=2,      # Fewer concurrent workers
)
```

### Slow Processing

```python
# Increase concurrency if I/O bound
config = BatchProcessingConfig(
    max_workers=16,
    batch_size=100,
)
```

## References

- `batch_processor.py`: Core implementation
- `indexing_with_batch.py`: Example integration
- `tests/test_batch_processor.py`: Unit tests

