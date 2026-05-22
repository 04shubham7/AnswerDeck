#!/usr/bin/env python
"""Simple standalone test for batch processor - no dependencies required."""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from batch_processor import (
    BatchProcessor,
    BatchProcessingConfig,
    ProcessingStatus,
)

def main():
    print("=" * 60)
    print("Batch Processor Quick Test")
    print("=" * 60)
    
    # Test 1: Basic processing
    print("\nTest 1: Basic Processing")
    config = BatchProcessingConfig(batch_size=2, max_workers=2, verbose=False)
    processor = BatchProcessor(config)
    
    def double(x):
        return x * 2
    
    items = [("a", 5), ("b", 10), ("c", 15)]
    progress = processor.process_items(items, double)
    
    print(f"  Items processed: {progress.processed_items}")
    print(f"  Successful: {progress.successful_items}")
    print(f"  Failed: {progress.failed_items}")
    print(f"  Status: {progress.status.value}")
    assert progress.successful_items == 3, "Expected 3 successful items"
    print("  ✓ PASSED")
    
    # Test 2: Error handling
    print("\nTest 2: Error Handling & Retry")
    attempts = {"count": 0}
    
    def retry_test(x):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ValueError("Not yet")
        return x
    
    config = BatchProcessingConfig(
        batch_size=1,
        max_workers=1,
        max_retries=3,
        retry_delay=0.01,
        verbose=False
    )
    processor = BatchProcessor(config)
    
    items = [("item", 10)]
    progress = processor.process_items(items, retry_test)
    
    print(f"  Attempts: {attempts['count']}")
    print(f"  Successful: {progress.successful_items}")
    assert progress.successful_items == 1, "Expected successful recovery from error"
    print("  ✓ PASSED")
    
    # Test 3: Configuration profiles
    print("\nTest 3: Configuration Profiles")
    from batch_config import get_config_by_profile
    
    profiles = ['document_indexing', 'cpu_bound', 'io_bound', 'development', 'production']
    for profile in profiles:
        cfg = get_config_by_profile(profile)
        print(f"  {profile}: batch_size={cfg.batch_size}, workers={cfg.max_workers}")
    print("  ✓ PASSED")
    
    # Test 4: Progress tracking
    print("\nTest 4: Progress Tracking")
    config = BatchProcessingConfig(batch_size=1, max_workers=1, verbose=False)
    processor = BatchProcessor(config)
    
    updates = []
    
    def track_progress(progress):
        updates.append(progress.processed_items)
    
    items = [("x", 1), ("y", 2), ("z", 3)]
    progress = processor.process_items(items, lambda x: x, on_progress=track_progress)
    
    print(f"  Progress updates: {len(updates)}")
    print(f"  Final percentage: {progress.progress_percentage}%")
    assert len(updates) == 3, "Expected 3 progress updates"
    assert progress.progress_percentage == 100.0, "Expected 100% completion"
    print("  ✓ PASSED")
    
    # Test 5: Success rate
    print("\nTest 5: Success Rate Calculation")
    config = BatchProcessingConfig(batch_size=1, max_workers=1, max_retries=0, verbose=False)
    processor = BatchProcessor(config)
    
    def sometimes_fail(x):
        if x == 2:
            raise ValueError("Item 2 fails")
        return x
    
    items = [("a", 1), ("b", 2), ("c", 3), ("d", 4)]
    progress = processor.process_items(items, sometimes_fail)
    
    rate = processor.success_rate
    print(f"  Success rate: {rate}%")
    print(f"  Successful: {progress.successful_items}")
    print(f"  Failed: {progress.failed_items}")
    assert rate == 75.0, "Expected 75% success rate"
    print("  ✓ PASSED")
    
    print("\n" + "=" * 60)
    print("All Tests Passed! ✓")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
