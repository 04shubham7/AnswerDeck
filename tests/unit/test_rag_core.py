"""Backend unit tests for RAG core components."""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.core.rag.embeddings.service import EmbeddingsService
from src.core.rag.search.service import SearchService
from src.core.rag.chat.service import ChatService


class TestEmbeddingsService:
    """Test embeddings service."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        with patch('src.core.rag.embeddings.service.config') as mock:
            mock.GOOGLE_API_KEY = 'test_key'
            mock.GOOGLE_EMBEDDING_MODEL = 'test_model'
            yield mock

    @pytest.fixture
    def embeddings_service(self, mock_config):
        """Create embeddings service with mocked dependencies."""
        with patch('src.core.rag.embeddings.service.GoogleGenerativeAIEmbeddings'):
            service = EmbeddingsService()
            service.model = Mock()
            return service

    def test_embed_text(self, embeddings_service):
        """Test embedding single text."""
        embeddings_service.model.embed_query = Mock(return_value=[0.1, 0.2, 0.3])
        result = embeddings_service.embed_text("test text")
        assert result == [0.1, 0.2, 0.3]
        embeddings_service.model.embed_query.assert_called_once_with("test text")

    def test_embed_texts(self, embeddings_service):
        """Test embedding multiple texts."""
        embeddings_service.model.embed_documents = Mock(
            return_value=[[0.1, 0.2], [0.3, 0.4]]
        )
        result = embeddings_service.embed_texts(["text1", "text2"])
        assert result == [[0.1, 0.2], [0.3, 0.4]]
        embeddings_service.model.embed_documents.assert_called_once()

    def test_embed_text_error(self, embeddings_service):
        """Test error handling in embedding."""
        embeddings_service.model.embed_query = Mock(
            side_effect=Exception("API Error")
        )
        with pytest.raises(Exception):
            embeddings_service.embed_text("test text")


class TestSearchService:
    """Test search service."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        with patch('src.core.rag.search.service.config') as mock:
            mock.QDRANT_URL = 'http://localhost:6333'
            mock.QDRANT_COLLECTION_NAME = 'test_collection'
            mock.SEARCH_RESULTS_K = 3
            yield mock

    @pytest.fixture
    def search_service(self, mock_config):
        """Create search service with mocked dependencies."""
        with patch('src.core.rag.search.service.QdrantVectorStore.from_existing_collection'):
            with patch('src.core.rag.search.service.get_embeddings_service'):
                service = SearchService()
                service.vector_store = Mock()
                return service

    def test_search(self, search_service):
        """Test search functionality."""
        mock_result = Mock()
        mock_result.page_content = "test content"
        mock_result.metadata = {"page_label": "1", "source": "test.pdf"}
        
        search_service.vector_store.similarity_search = Mock(return_value=[mock_result])
        result = search_service.search("test query")
        
        assert len(result) == 1
        assert result[0]["content"] == "test content"
        search_service.vector_store.similarity_search.assert_called_once()

    def test_search_custom_k(self, search_service):
        """Test search with custom k parameter."""
        search_service.vector_store.similarity_search = Mock(return_value=[])
        search_service.search("test", k=5)
        search_service.vector_store.similarity_search.assert_called_once_with("test", k=5)


class TestChatService:
    """Test chat service."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        with patch('src.core.rag.chat.service.config') as mock:
            mock.GOOGLE_API_KEY = 'test_key'
            mock.GOOGLE_CHAT_MODEL = 'test_model'
            yield mock

    @pytest.fixture
    def chat_service(self, mock_config):
        """Create chat service with mocked dependencies."""
        with patch('src.core.rag.chat.service.ChatGoogleGenerativeAI'):
            with patch('src.core.rag.chat.service.get_search_service'):
                service = ChatService()
                service.llm = Mock()
                service.search_service = Mock()
                return service

    def test_search_context(self, chat_service):
        """Test context search."""
        mock_result = {"content": "test", "metadata": {}, "page": "1", "source": "test.pdf"}
        chat_service.search_service.search = Mock(return_value=[mock_result])
        
        results, context = chat_service.search_context("test")
        assert len(results) == 1
        assert "test" in context

    def test_generate_response(self, chat_service):
        """Test response generation."""
        mock_response = Mock()
        mock_response.content = "Generated response"
        chat_service.llm.invoke = Mock(return_value=mock_response)
        
        response = chat_service.generate_response("query", "context")
        assert response == "Generated response"
        chat_service.llm.invoke.assert_called_once()

    def test_chat_full_flow(self, chat_service):
        """Test complete chat flow."""
        mock_result = {"content": "test", "metadata": {}, "page": "1", "source": "test.pdf"}
        chat_service.search_service.search = Mock(return_value=[mock_result])
        
        mock_response = Mock()
        mock_response.content = "Generated response"
        chat_service.llm.invoke = Mock(return_value=mock_response)
        
        result = chat_service.chat("test query")
        
        assert result["query"] == "test query"
        assert result["response"] == "Generated response"
        assert result["context_count"] == 1
