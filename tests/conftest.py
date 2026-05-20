"""Pytest configuration."""

import pytest
import os
from unittest.mock import patch


@pytest.fixture(autouse=True)
def setup_test_env():
    """Automatically setup test environment for each test."""
    os.environ['ENVIRONMENT'] = 'development'
    os.environ['GOOGLE_API_KEY'] = 'test_key_123'
    os.environ['QDRANT_URL'] = 'http://localhost:6333'
    os.environ['QDRANT_COLLECTION_NAME'] = 'test_collection'
    yield


@pytest.fixture
def mock_google_api():
    """Mock Google Generative AI API."""
    with patch('langchain_google_genai.GoogleGenerativeAIEmbeddings'):
        with patch('langchain_google_genai.ChatGoogleGenerativeAI'):
            yield


@pytest.fixture
def mock_qdrant():
    """Mock Qdrant vector store."""
    with patch('langchain_qdrant.QdrantVectorStore.from_existing_collection'):
        yield
