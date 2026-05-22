#!/usr/bin/env python
"""Verification script for batch processor implementation."""

import sys
import traceback


def test_imports():
    """Test that all batch processor modules can be imported."""
    print("Testing imports...")
    try:
        from batch_processor import (
            BatchProcessor,
            BatchProcessingConfig,
            ProcessingProgress,
            ProcessingStatus,
            ItemProcessingResult,
        )
        print("✓ batch_processor imports successful")
        
        from batch_config import get_config_by_profile
        print("✓ batch_config imports successful")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False


def test_basic_functionality():
    """Test basic batch processor functionality."""
    print("\nTesting basic functionality...")
    try:
        from batch_processor import BatchProcessor, BatchProcessingConfig
        
        config = BatchProcessingConfig(batch_size=2, max_workers=2)
        processor = BatchProcessor(config)
        
        def process_item(item):
            return item * 2
        
        items = [("item-1", 5), ("item-2", 10)]
        progress = processor.process_items(items, process_item)
        
        assert progress.successful_items == 2
        assert progress.failed_items == 0
        assert progress.total_items == 2
        
        print(f"✓ Processed {progress.successful_items} items successfully")
        return True
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling in batch processor."""
    print("\nTesting error handling...")
    try:
        from batch_processor import BatchProcessor, BatchProcessingConfig
        
        config = BatchProcessingConfig(
            batch_size=1,
            max_workers=1,
            max_retries=1,
            retry_delay=0.01,
        )
        processor = BatchProcessor(config)
        
        def failing_process(item):
            raise ValueError("Intentional error")
        
        items = [("item-1", 1)]
        progress = processor.process_items(items, failing_process)
        
        assert progress.failed_items == 1
        assert len(progress.error_messages) > 0
        
        print(f"✓ Error handling works correctly")
        print(f"  Failed items: {progress.failed_items}")
        print(f"  Error: {progress.error_messages[0][:50]}...")
        return True
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        traceback.print_exc()
        return False


def test_configuration_profiles():
    """Test configuration profiles."""
    print("\nTesting configuration profiles...")
    try:
        from batch_config import get_config_by_profile
        
        profiles = [
            'document_indexing',
            'cpu_bound',
            'io_bound',
            'development',
            'production',
        ]
        
        for profile in profiles:
            config = get_config_by_profile(profile)
            assert config.batch_size > 0
            assert config.max_workers > 0
            print(f"✓ Profile '{profile}': batch_size={config.batch_size}, workers={config.max_workers}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration profile test failed: {e}")
        traceback.print_exc()
        return False


def test_progress_tracking():
    """Test progress tracking functionality."""
    print("\nTesting progress tracking...")
    try:
        from batch_processor import (
            BatchProcessor,
            BatchProcessingConfig,
            ProcessingStatus,
        )
        import time
        
        config = BatchProcessingConfig(batch_size=1, max_workers=1)
        processor = BatchProcessor(config)
        
        updates = []
        
        def on_progress(progress):
            updates.append(progress.processed_items)
        
        def process_item(item):
            return item
        
        items = [("item-1", 1), ("item-2", 2), ("item-3", 3)]
        progress = processor.process_items(items, process_item, on_progress)
        
        assert len(updates) == 3
        assert progress.status == ProcessingStatus.COMPLETED
        assert progress.progress_percentage == 100.0
        
        print(f"✓ Progress tracking works correctly")
        print(f"  Total updates: {len(updates)}")
        print(f"  Final percentage: {progress.progress_percentage}%")
        return True
    except Exception as e:
        print(f"✗ Progress tracking test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("AnswerDeck Batch Processing System Verification")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Error Handling", test_error_handling),
        ("Configuration Profiles", test_configuration_profiles),
        ("Progress Tracking", test_progress_tracking),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
