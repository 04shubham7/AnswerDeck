"""Document processing pipeline for indexing."""

import logging
import time
from typing import List, Optional
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from src.config import get_config
from src.core.rag.embeddings.service import get_embeddings_service

logger = logging.getLogger(__name__)
config = get_config()


class IndexingPipeline:
    """Pipeline for processing and indexing documents."""
    
    def __init__(self):
        """Initialize indexing pipeline."""
        self.embeddings_service = get_embeddings_service()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.PDF_CHUNK_SIZE,
            chunk_overlap=config.PDF_CHUNK_OVERLAP
        )
        logger.info(f"Initialized indexing pipeline")
    
    def load_pdf(self, pdf_path: str) -> List[str]:
        """Load and split PDF document."""
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            loader = PyPDFLoader(str(pdf_file), mode="single")
            documents = loader.load()
            split_docs = self.text_splitter.split_documents(documents)
            logger.info(f"Loaded and split {len(split_docs)} chunks from {pdf_file.name}")
            return split_docs
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            raise
    
    def index_documents(self, documents: List, collection_name: Optional[str] = None, force_recreate: bool = False):
        """Index documents in Qdrant vector store."""
        if collection_name is None:
            collection_name = config.QDRANT_COLLECTION_NAME
        
        if not documents:
            logger.warning("No documents to index")
            return
        
        try:
            batch_size = config.PDF_BATCH_SIZE
            sleep_seconds = config.PDF_BATCH_SLEEP_SECONDS
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
                
                QdrantVectorStore.from_documents(
                    documents=batch,
                    embedding=self.embeddings_service.model,
                    url=config.QDRANT_URL,
                    collection_name=collection_name,
                    force_recreate=force_recreate and i == 0,
                )
                
                if i + batch_size < len(documents):
                    logger.info(f"Sleeping for {sleep_seconds} seconds to respect API limits")
                    time.sleep(sleep_seconds)
            
            logger.info(f"Successfully indexed {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise
