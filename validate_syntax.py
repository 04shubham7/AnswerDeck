#!/usr/bin/env python
"""Syntax validation script for batch processor implementation."""

import py_compile
import sys
from pathlib import Path


def validate_syntax(file_path):
    """Validate Python file syntax."""
    try:
        py_compile.compile(file_path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)


def main():
    files_to_check = [
        "batch_processor.py",
        "batch_config.py",
        "indexing_with_batch.py",
        "verify_batch_processor.py",
        "quick_test.py",
        "tests/test_batch_processor.py",
        "tests/test_smoke.py",
    ]
    
    print("=" * 60)
    print("Validating Python Syntax")
    print("=" * 60)
    
    all_valid = True
    for file_path in files_to_check:
        full_path = Path(file_path)
        if not full_path.exists():
            print(f"✗ {file_path}: FILE NOT FOUND")
            all_valid = False
            continue
        
        valid, error = validate_syntax(str(full_path))
        if valid:
            size = full_path.stat().st_size
            print(f"✓ {file_path}: OK ({size:,} bytes)")
        else:
            print(f"✗ {file_path}: SYNTAX ERROR")
            print(f"  {error}")
            all_valid = False
    
    print("=" * 60)
    if all_valid:
        print("All files have valid Python syntax! ✓")
        return 0
    else:
        print("Some files have syntax errors! ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
