#!/usr/bin/env python
"""Setup script to initialize directory structure for batch processing system."""
import os

# Define directory structure
DIRECTORIES = [
    "src",
    "src/core",
    "src/pipelines",
    "src/pipelines/indexing",
]

def setup_directories():
    """Create all necessary directories."""
    for directory in DIRECTORIES:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created: {directory}")

if __name__ == "__main__":
    setup_directories()
    print("\nDirectory structure initialized successfully!")
