"""Main entry point for backend CLI."""

import sys
import argparse
import logging
from src.logger import setup_logger
from src.config import get_config
from src.pipelines.indexing.processor import IndexingPipeline
from pathlib import Path

logger = setup_logger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='AnswerDeck CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index documents')
    index_parser.add_argument('pdf_path', help='Path to PDF file')
    index_parser.add_argument('--force-recreate', action='store_true', help='Force recreate collection')
    
    # Server command
    server_parser = subparsers.add_parser('serve', help='Start API server')
    server_parser.add_argument('--host', default='0.0.0.0', help='Server host')
    server_parser.add_argument('--port', type=int, default=8000, help='Server port')
    
    args = parser.parse_args()
    
    if args.command == 'index':
        pipeline = IndexingPipeline()
        config = get_config()
        logger.info(f"Indexing {args.pdf_path}")
        documents = pipeline.load_pdf(args.pdf_path)
        pipeline.index_documents(documents, force_recreate=args.force_recreate)
        logger.info("Indexing completed")
    
    elif args.command == 'serve':
        import uvicorn
        logger.info(f"Starting server on {args.host}:{args.port}")
        uvicorn.run(
            "src.api.server:app",
            host=args.host,
            port=args.port,
            reload=True
        )
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
