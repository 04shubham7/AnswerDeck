"""S3 document ingestion API routes."""

import os
import logging
import tempfile
from typing import Optional
import boto3
from botocore.config import Config
from botocore import UNSIGNED
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from src.pipelines.indexing.processor import IndexingPipeline

router = APIRouter(prefix="/api/v1/ingest", tags=["ingest"])
logger = logging.getLogger(__name__)


class S3IngestRequest(BaseModel):
    bucket_name: str = Field(..., description="The name of the S3 bucket")
    object_key: str = Field(..., description="The key of the PDF object in S3")
    aws_access_key_id: Optional[str] = Field(None, description="Optional AWS Access Key ID")
    aws_secret_access_key: Optional[str] = Field(None, description="Optional AWS Secret Access Key")
    aws_region: Optional[str] = Field(None, description="Optional AWS Region")
    collection_name: Optional[str] = Field(None, description="Optional Qdrant collection name")
    force_recreate: bool = Field(False, description="Whether to recreate the collection")


@router.post("/s3")
async def ingest_s3(request: S3IngestRequest):
    """Download a PDF from S3, split it, and index it in Qdrant."""
    logger.info(f"Received S3 ingestion request for s3://{request.bucket_name}/{request.object_key}")
    
    s3_args = {}
    if request.aws_access_key_id and request.aws_secret_access_key:
        s3_args["aws_access_key_id"] = request.aws_access_key_id
        s3_args["aws_secret_access_key"] = request.aws_secret_access_key
    if request.aws_region:
        s3_args["region_name"] = request.aws_region

    # If no credentials, try unsigned client config to allow downloading from public buckets
    try:
        if not request.aws_access_key_id and not os.getenv("AWS_ACCESS_KEY_ID"):
            config = Config(signature_version=UNSIGNED)
            s3_client = boto3.client('s3', config=config, **s3_args)
        else:
            s3_client = boto3.client('s3', **s3_args)
    except Exception as e:
        logger.error(f"Failed to create S3 client: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to initialize S3 client: {str(e)}")

    # Create temporary file
    try:
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        temp_path = temp_file.name
        temp_file.close()
    except Exception as e:
        logger.error(f"Failed to create temporary file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create temp file: {str(e)}")

    try:
        logger.info(f"Downloading from S3: {request.bucket_name}/{request.object_key}")
        s3_client.download_file(request.bucket_name, request.object_key, temp_path)
        logger.info(f"Download complete. Parsing PDF...")

        pipeline = IndexingPipeline()
        split_docs = pipeline.load_pdf(temp_path)
        
        # Override source metadata to point to S3 URI
        s3_uri = f"s3://{request.bucket_name}/{request.object_key}"
        for doc in split_docs:
            doc.metadata["source"] = s3_uri
            
        logger.info(f"Indexing {len(split_docs)} documents into Qdrant...")
        pipeline.index_documents(
            split_docs, 
            collection_name=request.collection_name, 
            force_recreate=request.force_recreate
        )
        
        logger.info(f"S3 Ingestion completed successfully for s3://{request.bucket_name}/{request.object_key}")
        return {
            "status": "success",
            "message": f"Successfully ingested {len(split_docs)} chunks from {s3_uri} into Qdrant",
            "chunks_count": len(split_docs),
            "source": s3_uri
        }
    except Exception as e:
        logger.error(f"S3 ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"S3 Ingestion failed: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {temp_path}: {e}")


@router.post("/file")
async def ingest_file(
    file: UploadFile = File(...),
    collection_name: Optional[str] = Form(None),
    force_recreate: bool = Form(False)
):
    """Upload a local PDF file and index it in Qdrant."""
    logger.info(f"Received file upload ingestion request for file: {file.filename}")
    
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    try:
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        temp_path = temp_file.name
        
        # Read uploaded content and write to temporary file
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process file upload: {str(e)}")
        
    try:
        pipeline = IndexingPipeline()
        split_docs = pipeline.load_pdf(temp_path)
        
        # Override source metadata to point to filename
        for doc in split_docs:
            doc.metadata["source"] = file.filename
            
        logger.info(f"Indexing {len(split_docs)} documents into Qdrant...")
        pipeline.index_documents(
            split_docs, 
            collection_name=collection_name, 
            force_recreate=force_recreate
        )
        
        logger.info(f"File Ingestion completed successfully for file: {file.filename}")
        return {
            "status": "success",
            "message": f"Successfully ingested {len(split_docs)} chunks from {file.filename} into Qdrant",
            "chunks_count": len(split_docs),
            "source": file.filename
        }
    except Exception as e:
        logger.error(f"Local file ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"File Ingestion failed: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {temp_path}: {e}")
