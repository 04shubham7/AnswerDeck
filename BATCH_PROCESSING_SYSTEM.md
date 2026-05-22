# Batch Processing System for AnswerDeck RAG

## Overview

The batch processing system is a robust, production-ready framework for parallel document processing in the AnswerDeck RAG (Retrieval-Augmented Generation) system. It enables efficient processing of large document collections with concurrent indexing, automatic error recovery, and comprehensive progress tracking.

## Features

### Core Capabilities

- **Parallel Processing**: Process multiple documents concurrently using ThreadPoolExecutor
- **Async Support**: Alternative async implementation using asyncio for non-blocking operations
- **Automatic Retries**: Failed items are automatically retried with configurable delays
- **Progress Tracking**: Real-time progress metrics and ETA calculations
- **Error Handling**: Comprehensive error capture and reporting
- **Cancellation Support**: Gracefully cancel ongoing operations
- **Rate Limiting**: Built-in support for APIs with rate limits
- **Configurable**: Extensive configuration options for different use cases

### Key Metrics

- Items processed per batch
- Concurrent worker count
- Success/failure rates
- Processing time per item
- Estimated time to completion
- Detailed error messages

## Quick Start

### Installation

The batch processor is included in the AnswerDeck codebase. No additional installation is needed.

### Basic Example

```python
from batch_processor import BatchProcessor, BatchProcessingConfig

# Configure batch processing
config = BatchProcessingConfig(
    batch_size=10,
    max_workers=4,
    max_retries=3,
    verbose=True,
)

# Create processor
processor = BatchProcessor(config)

# Define processing function
def process_document(doc):
    # Your processing logic
    return embedded_document

# Process documents
documents = [("doc-1", doc1), ("doc-2", doc2), ...]
progress = processor.process_items(documents, process_document)

# Check results
print(f"Success: {progress.successful_items}/{progress.total_items}")
print(f"Failed: {progress.failed_items}")
```

### With Progress Tracking

```python
def on_progress(progress):
    print(f"Progress: {progress.progress_percentage:.1f}%")
    print(f"Processed: {progress.processed_items}/{progress.total_items}")

progress = processor.process_items(
    documents,
    process_document,
    on_progress=on_progress
)
```

## Configuration Profiles

The system includes pre-configured profiles for common use cases:

### Document Indexing (API with Rate Limits)
```python
from batch_config import get_config_by_profile

config = get_config_by_profile('document_indexing')
# batch_size=10, max_workers=2, retry_delay=60s
```

### CPU-Bound Tasks
```python
config = get_config_by_profile('cpu_bound')
# batch_size=50, max_workers=4, longer timeouts
```

### I/O-Bound Tasks
```python
config = get_config_by_profile('io_bound')
# batch_size=100, max_workers=16
```

### Development
```python
config = get_config_by_profile('development')
# Smaller batches, verbose logging
```

### Production
```python
config = get_config_by_profile('production')
# Optimized for reliability, max_retries=5
```

## Architecture

### Components

1. **BatchProcessor**: Main orchestrator for batch processing
2. **BatchProcessingConfig**: Configuration management
3. **ProcessingProgress**: Progress tracking and metrics
4. **ItemProcessingResult**: Result information for each item
5. **ProcessingStatus**: State enumeration

### Processing Flow

```
Input Items
    ↓
[Validation]
    ↓
[Initial Processing] → [Retry Loop (if failures)]
    ↓
[Progress Updates] → [Callbacks]
    ↓
[Aggregation]
    ↓
[Final Results]
```

## Usage Examples

### Example 1: Document Embedding

```python
from batch_processor import BatchProcessor, BatchProcessingConfig
from langchain_google_genai import GoogleGenerativeAIEmbeddings

config = BatchProcessingConfig(
    batch_size=10,
    max_workers=2,
    max_retries=3,
    retry_delay=60.0,
    verbose=True,
)

processor = BatchProcessor(config)
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

def embed_document(doc):
    return embeddings.embed_query(doc.page_content)

documents = load_documents()
items = [(f"doc-{i}", doc) for i, doc in enumerate(documents)]

progress = processor.process_items(items, embed_document)

if progress.failed_items > 0:
    print(f"Warning: {progress.failed_items} documents failed to embed")
    for error in progress.error_messages[:5]:  # Show first 5 errors
        print(f"  - {error}")
```

### Example 2: Parallel Image Processing

```python
from pathlib import Path
from PIL import Image

config = BatchProcessingConfig(
    batch_size=50,
    max_workers=8,
    max_retries=2,
)

processor = BatchProcessor(config)

def process_image(image_path):
    img = Image.open(image_path)
    # Apply transformations
    processed = img.resize((256, 256))
    processed.save(f"output/{image_path.name}")
    return image_path.name

image_files = list(Path("images").glob("*.jpg"))
items = [(f.stem, f) for f in image_files]

progress = processor.process_items(items, process_image)
print(f"Processed {progress.successful_items} images successfully")
```

### Example 3: Async API Calls

```python
import asyncio
import aiohttp

config = BatchProcessingConfig(
    batch_size=100,
    max_workers=20,
    timeout_per_item=30.0,
)

processor = BatchProcessor(config)

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

urls = ["http://api.example.com/data/1", "http://api.example.com/data/2", ...]
items = [(f"url-{i}", url) for i, url in enumerate(urls)]

progress = await processor.process_items_async(items, fetch_data)
print(f"Success rate: {processor.success_rate:.1f}%")
```

## API Reference

See [BATCH_PROCESSING_API.md](BATCH_PROCESSING_API.md) for comprehensive API documentation.

## Testing

### Run Tests

```bash
# Run all tests
pytest tests/test_batch_processor.py -v

# Run specific test
pytest tests/test_batch_processor.py::TestBatchProcessor::test_basic_processing -v

# Run with coverage
pytest tests/test_batch_processor.py --cov=batch_processor
```

### Test Coverage

- Basic processing functionality
- Error handling and retry logic
- Progress tracking
- Concurrent processing
- Async operations
- Configuration validation
- Edge cases (empty items, timeouts, etc.)

## Performance Tuning

### Batch Size Guidelines

| Task Type | Recommended Size |
|-----------|-----------------|
| API calls with rate limits | 5-10 |
| Network I/O | 50-100 |
| Local processing | 50-100 |
| CPU-intensive | 20-50 |
| Memory-limited | 5-10 |

### Worker Count Guidelines

| Task Type | Formula |
|-----------|---------|
| CPU-bound | CPU count |
| I/O-bound | 2-3 × CPU count |
| Network | 10-100+ |
| GPU-based | GPU count |

### Example Configurations

#### For Slow APIs
```python
BatchProcessingConfig(
    batch_size=5,
    max_workers=1,        # Sequential to be safe
    retry_delay=120.0,    # 2 minutes between retries
    timeout_per_item=600.0,  # 10 minute timeout
)
```

#### For Fast Local Processing
```python
BatchProcessingConfig(
    batch_size=100,
    max_workers=8,        # CPU cores
    retry_delay=0.1,
    timeout_per_item=10.0,
)
```

#### For Large-Scale Processing
```python
BatchProcessingConfig(
    batch_size=200,
    max_workers=32,       # Many concurrent tasks
    retry_delay=1.0,
    timeout_per_item=300.0,
)
```

## Error Handling

### Common Issues

**High Failure Rate**
- Reduce concurrency: lower `max_workers`
- Increase timeouts: increase `timeout_per_item`
- Add more retries: increase `max_retries`
- Increase retry delay: increase `retry_delay`

**Memory Usage High**
- Reduce batch size: lower `batch_size`
- Reduce worker count: lower `max_workers`
- Check if items are being freed properly

**Rate Limit Errors**
- Reduce concurrency significantly
- Increase retry delay to match rate limit window
- Consider sequential processing (`max_workers=1`)

**Timeout Errors**
- Increase `timeout_per_item`
- Reduce `batch_size` or `max_workers`
- Investigate if processing function is actually slow

## Monitoring and Debugging

### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)

config = BatchProcessingConfig(verbose=True)
processor = BatchProcessor(config)
```

### Progress Callback for Monitoring

```python
def monitor_progress(progress):
    print(f"""
    Progress: {progress.processed_items}/{progress.total_items}
    Success: {progress.successful_items}
    Failed: {progress.failed_items}
    Elapsed: {progress.elapsed_time:.1f}s
    ETA: {progress.estimated_remaining_time:.1f}s
    Success Rate: {progress.success_rate:.1f}%
    """)

progress = processor.process_items(items, func, on_progress=monitor_progress)
```

### Check Results

```python
progress = processor.process_items(items, func)

if progress.failed_items > 0:
    print(f"Failed items: {progress.failed_items}")
    print("Error messages:")
    for error in progress.error_messages:
        print(f"  - {error}")
```

## Integration

### With Indexing Pipeline

The batch processor is integrated into `indexing_with_batch.py`:

```python
from batch_processor import BatchProcessor, BatchProcessingConfig

config = BatchProcessingConfig(
    batch_size=10,
    max_workers=2,
    max_retries=3,
    retry_delay=60.0,
)

processor = BatchProcessor(config)
progress = processor.process_items(documents, embed_function)
```

### Custom Integration

```python
from batch_processor import BatchProcessor, BatchProcessingConfig

class DocumentIndexer:
    def __init__(self, config=None):
        self.processor = BatchProcessor(config or BatchProcessingConfig())
    
    def index_documents(self, documents):
        items = [(f"doc-{i}", doc) for i, doc in enumerate(documents)]
        return self.processor.process_items(items, self._embed_document)
    
    def _embed_document(self, doc):
        # Your embedding logic
        return embeddings
```

## Files

- `batch_processor.py`: Core batch processing implementation
- `batch_config.py`: Configuration profiles
- `indexing_with_batch.py`: Example integration with document indexing
- `tests/test_batch_processor.py`: Comprehensive test suite
- `BATCH_PROCESSING_API.md`: Detailed API documentation
- `BATCH_PROCESSING_SYSTEM.md`: This file

## Contributing

When adding new features or modifying the batch processor:

1. Add corresponding tests in `tests/test_batch_processor.py`
2. Update documentation in `BATCH_PROCESSING_API.md`
3. Update configuration in `batch_config.py` if needed
4. Run full test suite: `pytest tests/test_batch_processor.py -v`
5. Check code quality: `pylint batch_processor.py`

## Future Enhancements

- [ ] Exponential backoff for retries
- [ ] Distributed processing support
- [ ] Advanced metrics collection
- [ ] Built-in monitoring dashboard
- [ ] Checkpoint/resume capabilities
- [ ] Priority queue support
- [ ] Dead letter queue for failed items
- [ ] Database storage of results

## License

Part of AnswerDeck RAG system.

## Support

For issues or questions:
1. Check [BATCH_PROCESSING_API.md](BATCH_PROCESSING_API.md) for API reference
2. Review example files for usage patterns
3. Check test file for implementation examples
4. Enable verbose logging for debugging

## References

- Python `concurrent.futures` documentation
- Python `asyncio` documentation
- LangChain documentation
- Qdrant documentation
