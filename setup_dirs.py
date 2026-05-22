"""Setup script to create directory structure and batch processor."""
import os
import sys

# Create directory structure
dirs = [
    "src",
    "src/core",
    "src/pipelines",
    "src/pipelines/indexing",
]

for dir_path in dirs:
    os.makedirs(dir_path, exist_ok=True)
    print(f"Created directory: {dir_path}")

print("Directory structure created successfully!")
