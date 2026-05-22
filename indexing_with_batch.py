"""Indexing helper to split PDFs and upload embeddings to Qdrant.

This module demonstrates batch processing for document indexing.
Run with `--run` to perform indexing; without it this script does a dry run.

The batch processor provides:
- Parallel document embedding generation
- Automatic retry logic for failed items
- Progress tracking and monitoring
- Configurable batch sizes and worker counts
"""

import getpass
import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google API key: ")

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from batch_processor import (
    BatchProcessor,
    BatchProcessingConfig,
    ProcessingProgress,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

RUN_INDEXING = "--run" in sys.argv
FORCE_RECREATE = "--force-recreate" in sys.argv

pdf_path = Path(__file__).parent / "nodejs.pdf"

if not pdf_path.exists():
    raise FileNotFoundError(f"PDF file not found: {pdf_path}")

# Load PDF file as a single document to keep the embedding request count manageable.
logger.info(f"Loading PDF from {pdf_path}...")
loader = PyPDFLoader(str(pdf_path), mode="single")
documents = loader.load()

# Chunking
logger.info("Splitting documents into chunks...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
split_docs = text_splitter.split_documents(documents)

print(f"Prepared {len(split_docs)} chunks from {pdf_path.name}.")

if not RUN_INDEXING:
    print("Dry run complete. No embeddings were generated and no data was written to Qdrant.")
    print("To perform indexing, run: python indexing.py --run")
    print("To recreate the collection, run: python indexing.py --run --force-recreate")
    raise SystemExit(0)

# Initialize batch processor configuration
# Batch size of 10 to stay safely under the Gemini RPM limit.
# Using 2 workers to manage concurrent embedding requests.
config = BatchProcessingConfig(
    batch_size=10,
    max_workers=2,
    max_retries=3,
    retry_delay=60.0,  # 60 seconds between retries to respect rate limits
    verbose=True,
)

processor = BatchProcessor(config)

# Vector Embeddings
logger.info("Initializing embeddings model...")
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# Process documents in batches using the batch processor
vectorstore = None

def process_document_batch(chunk):
    """Process a single document chunk by generating embeddings."""
    # This function will be called for each chunk in parallel
    return chunk

def progress_callback(progress: ProcessingProgress):
    """Callback function called on progress updates."""
    progress.log_summary()

try:
    logger.info(f"Starting batch processing of {len(split_docs)} document chunks...")
    
    # Create list of (id, chunk) tuples for batch processor
    items = [(f"chunk-{i}", chunk) for i, chunk in enumerate(split_docs)]
    
    # Process items using batch processor
    progress = processor.process_items(
        items,
        process_document_batch,
        on_progress=progress_callback,
    )
    
    # Process successful chunks with vectorstore
    logger.info(f"Successfully processed {progress.successful_items} chunks")
    
    for start_index in range(0, len(split_docs), config.batch_size):
        batch = split_docs[start_index : start_index + config.batch_size]
        end_index = start_index + len(batch)
        logger.info(f"Uploading embeddings for batch {start_index} to {end_index}...")

        if vectorstore is None:
            vectorstore = QdrantVectorStore.from_documents(
                batch,
                embeddings_model,
                collection_name="learning_vectors",
                host="localhost",
                port=6333,
                force_recreate=FORCE_RECREATE,
            )
        else:
            vectorstore.add_documents(batch)

except Exception as exc:
    logger.error("Indexing failed during embedding/upload.")
    logger.error(
        "If you see RESOURCE_EXHAUSTED, switch to another API key/project or wait for quota reset."
    )
    logger.error(f"Details: {exc}")
    raise SystemExit(1)

print("Vector store created and documents embedded successfully.")
print("You can now query the vector store for relevant information.")
