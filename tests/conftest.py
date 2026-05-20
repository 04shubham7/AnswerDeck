"""Test configuration and fixtures."""

import pytest
import os
from unittest.mock import patch


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment."""
    os.environ['ENVIRONMENT'] = 'development'
    os.environ['GOOGLE_API_KEY'] = 'test_key'
    os.environ['QDRANT_URL'] = 'http://localhost:6333'


@pytest.fixture
def mock_embeddings():
    """Mock embeddings model."""
    with patch('langchain_google_genai.GoogleGenerativeAIEmbeddings'):
        yield
