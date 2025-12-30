import argparse
import sys
from pathlib import Path
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings, validate_settings
from src.services.crawler import CrawlerService
from src.services.content_processor import ContentProcessor
from src.services.embedding_service import EmbeddingService
from src.services.vector_store import VectorStoreService
from src.logging_config import setup_logging


def create_parser():
    """
    Create the argument parser for the CLI
    """
    parser = argparse.ArgumentParser(
        description="RAG Website Ingestion Pipeline - Crawl, process, and store content for RAG systems"
    )

    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="The root URL of the Docusaurus book to ingest"
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=settings.chunk_size,
        help=f"Size of content chunks (default: {settings.chunk_size})"
    )

    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=settings.chunk_overlap,
        help=f"Overlap between chunks (default: {settings.chunk_overlap})"
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=settings.max_pages,
        help=f"Maximum number of pages to process (default: {settings.max_pages})"
    )

    parser.add_argument(
        "--collection-name",
        type=str,
        default=settings.collection_name,
        help=f"Qdrant collection name (default: {settings.collection_name})"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default=settings.log_level,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=f"Logging level (default: {settings.log_level})"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the pipeline without actually storing vectors"
    )

    return parser


def main():
    """
    Main CLI entry point
    """
    parser = create_parser()
    args = parser.parse_args()

    # Validate settings
    errors = validate_settings()
    if errors:
        print("Configuration errors detected:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    # Setup logging
    setup_logging(log_level=args.log_level)

    print(f"Starting RAG ingestion pipeline for: {args.url}")
    print(f"Configuration:")
    print(f"  Chunk size: {args.chunk_size}")
    print(f"  Chunk overlap: {args.chunk_overlap}")
    print(f"  Max pages: {args.max_pages}")
    print(f"  Collection: {args.collection_name}")
    print(f"  Dry run: {args.dry_run}")
    print()

    try:
        # Initialize services
        print("Initializing services...")
        crawler = CrawlerService(
            rate_limit_delay=settings.rate_limit_delay,
            max_pages=args.max_pages
        )

        processor = ContentProcessor(
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )

        embedding_service = EmbeddingService(
            api_key=settings.cohere_api_key
        )

        vector_store = VectorStoreService(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key,
            collection_name=args.collection_name
        )

        print("Services initialized successfully")
        print()

        # Step 1: Crawl the website
        print("Step 1: Crawling website...")
        urls = crawler.get_all_page_urls(args.url)
        print(f"Found {len(urls)} pages to process")

        # Step 2: Process each page
        print("Step 2: Processing pages...")
        all_chunks = []

        for i, url in enumerate(urls):
            print(f"  Processing page {i+1}/{len(urls)}: {url}")
            try:
                content = crawler.get_page_content(url)
                if content:
                    chunks = processor.process_file(url, content)
                    all_chunks.extend(chunks)
                    print(f"    Created {len(chunks)} chunks")
            except Exception as e:
                print(f"    Error processing {url}: {str(e)}")
                continue

        print(f"Total chunks created: {len(all_chunks)}")
        print()

        if args.dry_run:
            print("Dry run completed. No vectors were stored.")
            return

        # Step 3: Generate embeddings
        print("Step 3: Generating embeddings...")
        chunks_with_embeddings = embedding_service.process_chunks_with_embeddings(all_chunks)
        print(f"Embeddings generated for {len(chunks_with_embeddings)} chunks")
        print()

        # Step 4: Store in vector database
        print("Step 4: Storing in vector database...")
        success = vector_store.store_chunks(chunks_with_embeddings)
        if success:
            print("Successfully stored all vectors in Qdrant")
        else:
            print("Error storing vectors in Qdrant")

        print()
        print("Pipeline completed successfully!")

    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error during pipeline execution: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()