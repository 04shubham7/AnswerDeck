"""Integration tests for S3 ingestion API routes."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from src.api.server import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestS3IngestEndpoint:
    """Test S3 ingestion endpoint."""

    @patch('src.api.routes.ingest.boto3.client')
    @patch('src.api.routes.ingest.IndexingPipeline')
    def test_ingest_s3_success(self, mock_pipeline_class, mock_boto_client, client):
        """Test successful S3 PDF ingestion."""
        # Mock boto3 S3 client
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3

        # Mock IndexingPipeline
        mock_pipeline = Mock()
        mock_doc = Mock()
        mock_doc.metadata = {"source": "temp_file_path"}
        mock_pipeline.load_pdf = Mock(return_value=[mock_doc])
        mock_pipeline.index_documents = Mock()
        mock_pipeline_class.return_value = mock_pipeline

        # Request payload
        payload = {
            "bucket_name": "test-bucket",
            "object_key": "path/to/doc.pdf",
            "aws_access_key_id": "testkey",
            "aws_secret_access_key": "testsecret",
            "aws_region": "us-east-1",
            "collection_name": "test_collection",
            "force_recreate": True
        }

        response = client.post("/api/v1/ingest/s3", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["source"] == "s3://test-bucket/path/to/doc.pdf"
        assert data["chunks_count"] == 1
        
        # Verify that boto3 client downloaded the file
        mock_s3.download_file.assert_called_once()
        # Verify document source metadata was overridden
        assert mock_doc.metadata["source"] == "s3://test-bucket/path/to/doc.pdf"
        # Verify pipeline index was called
        mock_pipeline.index_documents.assert_called_once_with(
            [mock_doc],
            collection_name="test_collection",
            force_recreate=True
        )

    @patch('src.api.routes.ingest.boto3.client')
    def test_ingest_s3_client_creation_fail(self, mock_boto_client, client):
        """Test failure during boto3 client initialization."""
        mock_boto_client.side_effect = Exception("AWS Config Error")

        payload = {
            "bucket_name": "test-bucket",
            "object_key": "path/to/doc.pdf",
            "aws_access_key_id": "testkey",
            "aws_secret_access_key": "testsecret"
        }

        response = client.post("/api/v1/ingest/s3", json=payload)
        
        assert response.status_code == 400
        assert "Failed to initialize S3 client" in response.json()["detail"]

    @patch('src.api.routes.ingest.boto3.client')
    def test_ingest_s3_download_fail(self, mock_boto_client, client):
        """Test failure during S3 file download."""
        mock_s3 = Mock()
        mock_s3.download_file.side_effect = Exception("S3 Object Not Found")
        mock_boto_client.return_value = mock_s3

        payload = {
            "bucket_name": "test-bucket",
            "object_key": "nonexistent.pdf"
        }

        response = client.post("/api/v1/ingest/s3", json=payload)
        
        assert response.status_code == 500
        assert "S3 Ingestion failed" in response.json()["detail"]


class TestLocalFileIngestEndpoint:
    """Test local file ingestion endpoint."""

    @patch('src.api.routes.ingest.IndexingPipeline')
    def test_ingest_file_success(self, mock_pipeline_class, client):
        """Test successful local file upload and ingestion."""
        # Mock IndexingPipeline
        mock_pipeline = Mock()
        mock_doc = Mock()
        mock_doc.metadata = {"source": "temp_file_path"}
        mock_pipeline.load_pdf = Mock(return_value=[mock_doc])
        mock_pipeline.index_documents = Mock()
        mock_pipeline_class.return_value = mock_pipeline

        # Use bytes to simulate PDF file content
        file_content = b"%PDF-1.4 mock pdf data"
        files = {
            "file": ("test_doc.pdf", file_content, "application/pdf")
        }
        data = {
            "collection_name": "local_collection",
            "force_recreate": "true"
        }

        response = client.post("/api/v1/ingest/file", files=files, data=data)
        
        assert response.status_code == 200
        res_data = response.json()
        assert res_data["status"] == "success"
        assert res_data["source"] == "test_doc.pdf"
        assert res_data["chunks_count"] == 1
        
        # Verify metadata override
        assert mock_doc.metadata["source"] == "test_doc.pdf"
        # Verify pipeline index call
        mock_pipeline.index_documents.assert_called_once_with(
            [mock_doc],
            collection_name="local_collection",
            force_recreate=True
        )

    def test_ingest_file_invalid_type(self, client):
        """Test file ingestion with invalid file extension."""
        files = {
            "file": ("test_doc.txt", b"some plain text", "text/plain")
        }
        response = client.post("/api/v1/ingest/file", files=files)
        
        assert response.status_code == 400
        assert "Only PDF files are supported" in response.json()["detail"]
