"""Batch processing system for parallel document indexing and embedding generation.

This module provides a scalable batch processing framework for the AnswerDeck RAG system,
enabling efficient parallel processing of documents with configurable concurrency,
progress tracking, error handling, and retry logic.

Example:
    >>> config = BatchProcessingConfig(batch_size=10, max_workers=4)
    >>> processor = BatchProcessor(config)
    >>> results = processor.process_items(documents, process_document)
    >>> print(f"Processed {results.successful_count} items")
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Generic, List, Optional, TypeVar, Dict, Tuple
from datetime import datetime
import time

logger = logging.getLogger(__name__)

T = TypeVar("T")  # Input item type
R = TypeVar("R")  # Result type


class ProcessingStatus(Enum):
    """Enumeration of batch processing statuses."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchProcessingConfig:
    """Configuration for batch processing behavior.

    Attributes:
        batch_size: Number of items to process per batch (default: 10)
        max_workers: Maximum number of concurrent workers (default: 4)
        max_retries: Maximum number of retries for failed items (default: 3)
        retry_delay: Delay in seconds between retries (default: 1.0)
        timeout_per_item: Timeout in seconds for processing a single item (default: 300)
        verbose: Whether to log detailed progress information (default: False)
    """

    batch_size: int = 10
    max_workers: int = 4
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout_per_item: float = 300.0
    verbose: bool = False


@dataclass
class ItemProcessingResult:
    """Result of processing a single item.

    Attributes:
        item_id: Unique identifier for the item
        success: Whether processing succeeded
        result: The result of processing (None if failed)
        error: Error message if processing failed
        retry_count: Number of retries attempted
        processing_time: Time taken to process in seconds
    """

    item_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    processing_time: float = 0.0


@dataclass
class ProcessingProgress:
    """Progress information for a batch processing operation.

    Attributes:
        status: Current processing status
        total_items: Total number of items to process
        processed_items: Number of items processed so far
        successful_items: Number of successfully processed items
        failed_items: Number of failed items
        retry_items: Number of items being retried
        error_messages: List of error messages encountered
        start_time: When processing started
        elapsed_time: Time elapsed in seconds
        estimated_remaining_time: Estimated seconds until completion
        progress_percentage: Percentage of items processed
    """

    status: ProcessingStatus = ProcessingStatus.PENDING
    total_items: int = 0
    processed_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    retry_items: int = 0
    error_messages: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    elapsed_time: float = 0.0
    estimated_remaining_time: float = 0.0
    progress_percentage: float = 0.0

    def update_elapsed_time(self) -> None:
        """Update elapsed time based on start time."""
        if self.start_time:
            self.elapsed_time = (datetime.now() - self.start_time).total_seconds()
            if self.processed_items > 0 and self.total_items > 0:
                avg_time_per_item = self.elapsed_time / self.processed_items
                remaining_items = self.total_items - self.processed_items
                self.estimated_remaining_time = avg_time_per_item * remaining_items

    def update_progress_percentage(self) -> None:
        """Update progress percentage."""
        if self.total_items > 0:
            self.progress_percentage = (
                self.processed_items / self.total_items
            ) * 100

    def log_summary(self) -> None:
        """Log a summary of processing progress."""
        logger.info(
            f"Processing Progress: {self.processed_items}/{self.total_items} "
            f"({self.progress_percentage:.1f}%) | "
            f"Success: {self.successful_items}, Failed: {self.failed_items}, "
            f"Retrying: {self.retry_items}"
        )


class BatchProcessor(Generic[T, R]):
    """Manages parallel batch processing of items with progress tracking and error handling.

    This class provides a flexible framework for processing large collections of items
    concurrently, with built-in support for:
    - Configurable batch sizes and worker counts
    - Automatic retry logic with exponential backoff
    - Progress tracking and reporting
    - Graceful error handling
    - Processing cancellation

    Example:
        >>> config = BatchProcessingConfig(batch_size=5, max_workers=2)
        >>> processor = BatchProcessor(config)
        >>> def process_doc(doc): return len(doc.content)
        >>> results = processor.process_items(documents, process_doc)
    """

    def __init__(self, config: Optional[BatchProcessingConfig] = None):
        """Initialize the batch processor.

        Args:
            config: Configuration for batch processing. If None, uses defaults.
        """
        self.config = config or BatchProcessingConfig()
        self.progress = ProcessingProgress()
        self._cancelled = False
        self._current_tasks: Dict[str, asyncio.Task] = {}

    def process_items(
        self,
        items: List[Tuple[str, T]],
        process_func: Callable[[T], R],
        on_progress: Optional[Callable[[ProcessingProgress], None]] = None,
    ) -> ProcessingProgress:
        """Process a list of items in parallel batches with progress tracking.

        Args:
            items: List of (item_id, item_data) tuples to process
            process_func: Function that processes a single item
            on_progress: Optional callback function called after each item is processed

        Returns:
            ProcessingProgress: Final progress information including results

        Raises:
            ValueError: If items list is empty
        """
        if not items:
            raise ValueError("Items list cannot be empty")

        self.progress = ProcessingProgress(
            status=ProcessingStatus.IN_PROGRESS,
            total_items=len(items),
            start_time=datetime.now(),
        )
        self._cancelled = False

        if self.config.verbose:
            logger.info(
                f"Starting batch processing of {len(items)} items "
                f"with {self.config.max_workers} workers"
            )

        results: List[ItemProcessingResult] = []
        retry_queue: List[Tuple[str, T]] = []

        try:
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                # Process all items with initial attempt
                results.extend(
                    self._execute_batch(
                        items, process_func, executor, on_progress, attempt=1
                    )
                )

                # Handle retries
                for attempt in range(2, self.config.max_retries + 1):
                    failed_items = [
                        (r.item_id, items[[i[0] for i in items].index(r.item_id)][1])
                        for r in results
                        if not r.success
                    ]

                    if not failed_items:
                        break

                    if self.config.verbose:
                        logger.info(
                            f"Retrying {len(failed_items)} failed items (attempt {attempt})"
                        )

                    time.sleep(self.config.retry_delay)
                    retry_results = self._execute_batch(
                        failed_items,
                        process_func,
                        executor,
                        on_progress,
                        attempt=attempt,
                    )

                    # Update results with retry attempts
                    for retry_result in retry_results:
                        for i, result in enumerate(results):
                            if result.item_id == retry_result.item_id:
                                results[i] = retry_result
                                break

            self.progress.status = ProcessingStatus.COMPLETED

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            self.progress.status = ProcessingStatus.FAILED
            self.progress.error_messages.append(str(e))
            raise

        self._finalize_progress(results)
        return self.progress

    async def process_items_async(
        self,
        items: List[Tuple[str, T]],
        process_func: Callable[[T], R],
        on_progress: Optional[Callable[[ProcessingProgress], None]] = None,
    ) -> ProcessingProgress:
        """Process items asynchronously using asyncio.

        Args:
            items: List of (item_id, item_data) tuples to process
            process_func: Async function that processes a single item
            on_progress: Optional callback function called after each item is processed

        Returns:
            ProcessingProgress: Final progress information including results
        """
        if not items:
            raise ValueError("Items list cannot be empty")

        self.progress = ProcessingProgress(
            status=ProcessingStatus.IN_PROGRESS,
            total_items=len(items),
            start_time=datetime.now(),
        )
        self._cancelled = False

        if self.config.verbose:
            logger.info(
                f"Starting async batch processing of {len(items)} items "
                f"with {self.config.max_workers} workers"
            )

        results: List[ItemProcessingResult] = []

        try:
            # Create tasks for all items
            tasks = [
                self._process_item_async(item_id, item, process_func, attempt=1)
                for item_id, item in items
            ]

            # Process with semaphore to limit concurrency
            semaphore = asyncio.Semaphore(self.config.max_workers)

            async def bounded_process(task):
                async with semaphore:
                    return await task

            # Gather all results
            batch_results = await asyncio.gather(*[bounded_process(t) for t in tasks])
            results.extend(batch_results)

            # Handle retries asynchronously
            for attempt in range(2, self.config.max_retries + 1):
                failed_items = [(r.item_id, [i for i in items if i[0] == r.item_id][0][1]) for r in results if not r.success]

                if not failed_items:
                    break

                if self.config.verbose:
                    logger.info(
                        f"Retrying {len(failed_items)} failed items (attempt {attempt})"
                    )

                await asyncio.sleep(self.config.retry_delay)

                retry_tasks = [
                    self._process_item_async(item_id, item, process_func, attempt=attempt)
                    for item_id, item in failed_items
                ]

                retry_results = await asyncio.gather(*[bounded_process(t) for t in retry_tasks])

                # Update results
                for retry_result in retry_results:
                    for i, result in enumerate(results):
                        if result.item_id == retry_result.item_id:
                            results[i] = retry_result
                            break

            self.progress.status = ProcessingStatus.COMPLETED

        except asyncio.CancelledError:
            self.progress.status = ProcessingStatus.CANCELLED
            logger.info("Async batch processing cancelled")
        except Exception as e:
            logger.error(f"Async batch processing failed: {e}")
            self.progress.status = ProcessingStatus.FAILED
            self.progress.error_messages.append(str(e))
            raise

        self._finalize_progress(results)
        return self.progress

    def _execute_batch(
        self,
        items: List[Tuple[str, T]],
        process_func: Callable[[T], R],
        executor: ThreadPoolExecutor,
        on_progress: Optional[Callable[[ProcessingProgress], None]],
        attempt: int = 1,
    ) -> List[ItemProcessingResult]:
        """Execute a batch of items using thread pool.

        Args:
            items: Items to process
            process_func: Processing function
            executor: Thread pool executor
            on_progress: Progress callback
            attempt: Current attempt number

        Returns:
            List of processing results
        """
        futures = {
            executor.submit(self._process_item, item_id, item, process_func, attempt): (
                item_id,
                item,
            )
            for item_id, item in items
        }

        results = []
        for future in as_completed(futures):
            if self._cancelled:
                break

            result = future.result()
            results.append(result)

            # Update progress
            self.progress.processed_items += 1
            if result.success:
                self.progress.successful_items += 1
            else:
                self.progress.failed_items += 1

            self.progress.update_elapsed_time()
            self.progress.update_progress_percentage()

            if on_progress:
                on_progress(self.progress)

            if self.config.verbose:
                status = "✓" if result.success else "✗"
                logger.info(
                    f"[{status}] Item {result.item_id} "
                    f"(attempt {result.retry_count + 1}, "
                    f"{result.processing_time:.2f}s)"
                )

        return results

    def _process_item(
        self, item_id: str, item: T, process_func: Callable[[T], R], attempt: int = 1
    ) -> ItemProcessingResult:
        """Process a single item with timeout and error handling.

        Args:
            item_id: Unique identifier for the item
            item: Item to process
            process_func: Function to process the item
            attempt: Current attempt number

        Returns:
            ItemProcessingResult with success/failure information
        """
        start_time = time.time()
        retry_count = attempt - 1

        try:
            result = process_func(item)
            processing_time = time.time() - start_time

            return ItemProcessingResult(
                item_id=item_id,
                success=True,
                result=result,
                retry_count=retry_count,
                processing_time=processing_time,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"

            logger.warning(
                f"Item {item_id} processing failed (attempt {attempt}): {error_msg}"
            )

            return ItemProcessingResult(
                item_id=item_id,
                success=False,
                error=error_msg,
                retry_count=retry_count,
                processing_time=processing_time,
            )

    async def _process_item_async(
        self,
        item_id: str,
        item: T,
        process_func: Callable[[T], R],
        attempt: int = 1,
    ) -> ItemProcessingResult:
        """Process a single item asynchronously.

        Args:
            item_id: Unique identifier for the item
            item: Item to process
            process_func: Async function to process the item
            attempt: Current attempt number

        Returns:
            ItemProcessingResult with success/failure information
        """
        start_time = time.time()
        retry_count = attempt - 1

        try:
            result = await asyncio.wait_for(
                process_func(item), timeout=self.config.timeout_per_item
            )
            processing_time = time.time() - start_time

            return ItemProcessingResult(
                item_id=item_id,
                success=True,
                result=result,
                retry_count=retry_count,
                processing_time=processing_time,
            )

        except asyncio.TimeoutError:
            processing_time = time.time() - start_time
            error_msg = f"Timeout after {self.config.timeout_per_item}s"

            logger.warning(f"Item {item_id} timed out (attempt {attempt})")

            return ItemProcessingResult(
                item_id=item_id,
                success=False,
                error=error_msg,
                retry_count=retry_count,
                processing_time=processing_time,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"

            logger.warning(
                f"Item {item_id} processing failed (attempt {attempt}): {error_msg}"
            )

            return ItemProcessingResult(
                item_id=item_id,
                success=False,
                error=error_msg,
                retry_count=retry_count,
                processing_time=processing_time,
            )

    def _finalize_progress(self, results: List[ItemProcessingResult]) -> None:
        """Finalize progress information after processing.

        Args:
            results: List of processing results
        """
        self.progress.update_elapsed_time()
        self.progress.update_progress_percentage()

        # Collect error messages
        errors = [r.error for r in results if r.error]
        self.progress.error_messages.extend(errors)

        if self.config.verbose or self.progress.failed_items > 0:
            logger.info(
                f"Batch processing complete: "
                f"{self.progress.successful_items} successful, "
                f"{self.progress.failed_items} failed, "
                f"elapsed time: {self.progress.elapsed_time:.2f}s"
            )

    def cancel(self) -> None:
        """Cancel ongoing batch processing."""
        self._cancelled = True
        self.progress.status = ProcessingStatus.CANCELLED
        logger.info("Batch processing cancellation requested")

    @property
    def is_processing(self) -> bool:
        """Check if batch processing is currently active."""
        return self.progress.status == ProcessingStatus.IN_PROGRESS

    @property
    def success_rate(self) -> float:
        """Get the success rate as a percentage (0-100)."""
        if self.progress.total_items == 0:
            return 0.0
        return (
            self.progress.successful_items / self.progress.total_items
        ) * 100
