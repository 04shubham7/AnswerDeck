"""Configuration module for AnswerDeck RAG batch processing system.

This module provides centralized configuration for batch processing operations,
including profiles for different use cases and environments.
"""

from batch_processor import BatchProcessingConfig


# Default configurations for different use cases

# Configuration for document indexing with API rate limiting
DOCUMENT_INDEXING_CONFIG = BatchProcessingConfig(
    batch_size=10,
    max_workers=2,
    max_retries=3,
    retry_delay=60.0,  # 60 seconds between retries for API rate limits
    timeout_per_item=300.0,
    verbose=True,
)

# Configuration for CPU-intensive tasks
CPU_BOUND_CONFIG = BatchProcessingConfig(
    batch_size=50,
    max_workers=4,  # Match CPU core count
    max_retries=2,
    retry_delay=1.0,
    timeout_per_item=600.0,  # 10 minutes for long operations
    verbose=False,
)

# Configuration for I/O-bound tasks (network requests, file operations)
IO_BOUND_CONFIG = BatchProcessingConfig(
    batch_size=100,
    max_workers=16,  # More workers for I/O operations
    max_retries=3,
    retry_delay=2.0,
    timeout_per_item=300.0,
    verbose=False,
)

# Configuration for development/testing
DEVELOPMENT_CONFIG = BatchProcessingConfig(
    batch_size=5,
    max_workers=2,
    max_retries=1,
    retry_delay=0.5,
    timeout_per_item=60.0,
    verbose=True,
)

# Configuration for production with high reliability
PRODUCTION_CONFIG = BatchProcessingConfig(
    batch_size=20,
    max_workers=4,
    max_retries=5,
    retry_delay=3.0,
    timeout_per_item=300.0,
    verbose=False,
)


def get_config_by_profile(profile: str) -> BatchProcessingConfig:
    """Get batch processing configuration by profile name.
    
    Args:
        profile: Configuration profile name. One of:
            - 'document_indexing': For API-based document indexing
            - 'cpu_bound': For CPU-intensive tasks
            - 'io_bound': For I/O operations
            - 'development': For development/testing
            - 'production': For production deployments
    
    Returns:
        BatchProcessingConfig: Configuration for the specified profile
        
    Raises:
        ValueError: If profile name is not recognized
    """
    profiles = {
        'document_indexing': DOCUMENT_INDEXING_CONFIG,
        'cpu_bound': CPU_BOUND_CONFIG,
        'io_bound': IO_BOUND_CONFIG,
        'development': DEVELOPMENT_CONFIG,
        'production': PRODUCTION_CONFIG,
    }
    
    if profile not in profiles:
        raise ValueError(
            f"Unknown profile '{profile}'. Available profiles: "
            f"{', '.join(profiles.keys())}"
        )
    
    return profiles[profile]
