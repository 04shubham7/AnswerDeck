"""Smoke tests for basic functionality."""

import pytest
from src.config import get_config, DevelopmentConfig, ProductionConfig


def test_config_loading():
    """Test that configuration loads properly."""
    config = get_config()
    assert config is not None
    assert config.API_HOST
    assert config.API_PORT


def test_development_config():
    """Test development configuration."""
    config = DevelopmentConfig()
    assert config.DEBUG is True


def test_production_config():
    """Test production configuration."""
    config = ProductionConfig()
    assert config.DEBUG is False


def test_imports():
    """Test that all modules can be imported."""
    from src.api.server import create_app
    from src.core.rag.embeddings.service import get_embeddings_service
    from src.core.rag.search.service import get_search_service
    from src.core.rag.chat.service import get_chat_service
    from src.pipelines.indexing.processor import IndexingPipeline
    
    assert callable(create_app)
    assert callable(get_embeddings_service)
    assert callable(get_search_service)
    assert callable(get_chat_service)
