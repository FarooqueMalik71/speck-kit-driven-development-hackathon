#!/usr/bin/env python3
"""One-time textbook content ingestion script.
Run manually: cd backend && python ingest_textbook.py
NOT triggered on server startup."""

import sys
import os
import logging
from pathlib import Path

# Setup paths
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir / "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")


def main():
    # Import after path setup
    from src.config import settings
    from src.services.embedding_service import EmbeddingService
    from src.services.vector_store import VectorStoreService
    from src.services.content_processor import ContentProcessor

    # Validate required keys
    if not settings.cohere_api_key:
        logger.error("COHERE_API_KEY is required. Set it in backend/.env")
        sys.exit(1)
    if not settings.qdrant_api_key:
        logger.error("QDRANT_API_KEY is required. Set it in backend/.env")
        sys.exit(1)

    # Find all markdown files in frontend/docs/
    docs_dir = backend_dir.parent / "frontend" / "docs"
    if not docs_dir.exists():
        logger.error(f"Docs directory not found: {docs_dir}")
        sys.exit(1)

    md_files = sorted(docs_dir.rglob("*.md"))
    # Exclude tutorial-basics and tutorial-extras (Docusaurus defaults, not textbook content)
    md_files = [
        f for f in md_files
        if "tutorial-basics" not in str(f) and "tutorial-extras" not in str(f)
    ]

    print(f"Found {len(md_files)} textbook markdown files")

    if not md_files:
        logger.error("No markdown files found in frontend/docs/")
        sys.exit(1)

    # Initialize services
    embedding_service = EmbeddingService(api_key=settings.cohere_api_key)
    vector_store = VectorStoreService()
    content_processor = ContentProcessor(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )

    # Process each file into chunks
    all_chunks = []
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            relative_path = str(md_file.relative_to(docs_dir))
            chunks = content_processor.process_file(relative_path, content)
            all_chunks.extend(chunks)
            print(f"  {relative_path}: {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Error processing {md_file}: {e}")
            continue

    print(f"Total chunks: {len(all_chunks)}")

    if not all_chunks:
        logger.error("No chunks generated. Check markdown file contents.")
        sys.exit(1)

    # Generate embeddings and store in Qdrant
    print("Generating embeddings (this may take a minute)...")
    embedding_vectors = embedding_service.process_chunks_with_embeddings(all_chunks)
    print(f"Generated {len(embedding_vectors)} embedding vectors")

    print("Storing in Qdrant...")
    success = vector_store.store_chunks(embedding_vectors)
    print(f"Ingestion {'succeeded' if success else 'FAILED'}")

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
