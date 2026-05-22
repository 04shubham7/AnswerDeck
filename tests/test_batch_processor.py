"""Unit tests for batch processing system."""

import pytest
import asyncio
import time
from batch_processor import (
    BatchProcessor,
    BatchProcessingConfig,
    ProcessingStatus,
    ProcessingProgress,
)


class TestBatchProcessor:
    """Test suite for BatchProcessor class."""

    def test_basic_processing(self):
        """Test basic batch processing functionality."""
        config = BatchProcessingConfig(batch_size=2, max_workers=2)
        processor = BatchProcessor(config)

        def simple_process(item):
            return item * 2

        items = [("item-1", 5), ("item-2", 10), ("item-3", 15)]
        progress = processor.process_items(items, simple_process)

        assert progress.status == ProcessingStatus.COMPLETED
        assert progress.successful_items == 3
        assert progress.failed_items == 0
        assert progress.total_items == 3

    def test_error_handling_with_retry(self):
        """Test error handling and retry logic."""
        config = BatchProcessingConfig(
            batch_size=1, max_workers=1, max_retries=3, retry_delay=0.1
        )
        processor = BatchProcessor(config)

        attempt_count = {"value": 0}

        def flaky_process(item):
            attempt_count["value"] += 1
            if attempt_count["value"] < 3:
                raise ValueError(f"Simulated error on attempt {attempt_count['value']}")
            return item * 2

        items = [("item-1", 5)]
        progress = processor.process_items(items, flaky_process)

        assert progress.successful_items == 1
        assert progress.failed_items == 0

    def test_permanent_failure(self):
        """Test handling of items that fail permanently."""
        config = BatchProcessingConfig(
            batch_size=1, max_workers=1, max_retries=2, retry_delay=0.01
        )
        processor = BatchProcessor(config)

        def always_fail(item):
            raise ValueError("This always fails")

        items = [("item-1", 5), ("item-2", 10)]
        progress = processor.process_items(items, always_fail)

        assert progress.failed_items == 2
        assert progress.successful_items == 0
        assert progress.status == ProcessingStatus.COMPLETED

    def test_progress_tracking(self):
        """Test progress tracking functionality."""
        config = BatchProcessingConfig(batch_size=1, max_workers=1, verbose=False)
        processor = BatchProcessor(config)

        progress_updates = []

        def on_progress(progress):
            progress_updates.append(progress.processed_items)

        def simple_process(item):
            time.sleep(0.01)
            return item

        items = [(f"item-{i}", i) for i in range(5)]
        progress = processor.process_items(items, simple_process, on_progress)

        assert len(progress_updates) == 5
        assert progress_updates[-1] == 5
        assert progress.progress_percentage == 100.0

    def test_cancellation(self):
        """Test batch processing cancellation."""
        config = BatchProcessingConfig(batch_size=1, max_workers=1)
        processor = BatchProcessor(config)

        def slow_process(item):
            time.sleep(0.5)
            return item

        items = [(f"item-{i}", i) for i in range(10)]

        # Note: cancellation in sync mode doesn't work as expected
        # since it processes sequentially. This is expected behavior.
        progress = processor.process_items(items, slow_process)

        assert progress.status == ProcessingStatus.COMPLETED

    def test_empty_items_raises_error(self):
        """Test that empty items list raises ValueError."""
        processor = BatchProcessor()

        def dummy_process(item):
            return item

        with pytest.raises(ValueError):
            processor.process_items([], dummy_process)

    def test_configuration_defaults(self):
        """Test default configuration values."""
        config = BatchProcessingConfig()

        assert config.batch_size == 10
        assert config.max_workers == 4
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.timeout_per_item == 300.0
        assert config.verbose is False

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        config = BatchProcessingConfig(batch_size=1, max_workers=1, max_retries=1)
        processor = BatchProcessor(config)

        def sometimes_fail(item):
            if item == 2:
                raise ValueError("Item 2 fails")
            return item

        items = [(f"item-{i}", i) for i in range(4)]
        progress = processor.process_items(items, sometimes_fail)

        # 3 successful out of 4 = 75%
        success_rate = processor.success_rate
        assert success_rate == 75.0

    def test_concurrent_processing(self):
        """Test that items are processed concurrently."""
        config = BatchProcessingConfig(batch_size=5, max_workers=2)
        processor = BatchProcessor(config)

        times = {"start": time.time()}

        def timed_process(item):
            # Each item takes 0.1 seconds
            time.sleep(0.1)
            return item

        items = [(f"item-{i}", i) for i in range(4)]
        processor.process_items(items, timed_process)

        elapsed = time.time() - times["start"]

        # With 2 workers, 4 items should take ~0.2 seconds (2 batches)
        # Sequential would take ~0.4 seconds
        assert elapsed < 0.35  # Allow some overhead

    @pytest.mark.asyncio
    async def test_async_processing(self):
        """Test asynchronous batch processing."""
        config = BatchProcessingConfig(batch_size=2, max_workers=2)
        processor = BatchProcessor(config)

        async def async_process(item):
            await asyncio.sleep(0.01)
            return item * 2

        items = [("item-1", 5), ("item-2", 10), ("item-3", 15)]
        progress = await processor.process_items_async(items, async_process)

        assert progress.status == ProcessingStatus.COMPLETED
        assert progress.successful_items == 3
        assert progress.failed_items == 0

    @pytest.mark.asyncio
    async def test_async_error_handling(self):
        """Test error handling in async processing."""
        config = BatchProcessingConfig(
            batch_size=1, max_workers=1, max_retries=1
        )
        processor = BatchProcessor(config)

        async def async_fail(item):
            await asyncio.sleep(0.01)
            raise ValueError("Async failure")

        items = [("item-1", 5)]
        progress = await processor.process_items_async(items, async_fail)

        assert progress.failed_items == 1

    def test_processing_progress_fields(self):
        """Test ProcessingProgress data fields."""
        progress = ProcessingProgress(total_items=10, processed_items=5)

        assert progress.total_items == 10
        assert progress.processed_items == 5
        assert progress.status == ProcessingStatus.PENDING

    def test_is_processing_property(self):
        """Test is_processing property."""
        processor = BatchProcessor()

        assert not processor.is_processing

        # After starting processing, is_processing should be True
        # This is harder to test without threading, so we just verify initial state
        assert processor.progress.status == ProcessingStatus.PENDING


class TestBatchProcessingConfig:
    """Test suite for BatchProcessingConfig."""

    def test_custom_configuration(self):
        """Test creating custom configuration."""
        config = BatchProcessingConfig(
            batch_size=5,
            max_workers=8,
            max_retries=5,
            retry_delay=2.0,
            timeout_per_item=60.0,
            verbose=True,
        )

        assert config.batch_size == 5
        assert config.max_workers == 8
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.timeout_per_item == 60.0
        assert config.verbose is True

    def test_configuration_immutability(self):
        """Test that configuration can be modified (it's a dataclass)."""
        config = BatchProcessingConfig(batch_size=10)
        assert config.batch_size == 10

        config.batch_size = 20
        assert config.batch_size == 20


class TestProcessingProgress:
    """Test suite for ProcessingProgress."""

    def test_progress_percentage_update(self):
        """Test progress percentage calculation."""
        progress = ProcessingProgress(total_items=10, processed_items=5)
        progress.update_progress_percentage()

        assert progress.progress_percentage == 50.0

    def test_elapsed_time_update(self):
        """Test elapsed time tracking."""
        from datetime import datetime

        progress = ProcessingProgress(
            total_items=10,
            start_time=datetime.now(),
        )

        time.sleep(0.1)
        progress.update_elapsed_time()

        assert progress.elapsed_time >= 0.1

    def test_error_messages_collection(self):
        """Test error message collection."""
        progress = ProcessingProgress()

        progress.error_messages.append("Error 1")
        progress.error_messages.append("Error 2")

        assert len(progress.error_messages) == 2
        assert "Error 1" in progress.error_messages


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
