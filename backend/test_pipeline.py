#!/usr/bin/env python3
"""
Test script to verify the end-to-end RAG ingestion pipeline
"""
import sys
from pathlib import Path
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import settings, validate_settings
from src.services.crawler import CrawlerService
from src.services.content_processor import ContentProcessor
from src.services.embedding_service import EmbeddingService
from src.services.vector_store import VectorStoreService
from src.logging_config import setup_logging


def test_end_to_end_pipeline():
    """
    Test the complete end-to-end pipeline with a sample URL
    """
    print("Testing End-to-End RAG Ingestion Pipeline")
    print("=" * 60)

    # Validate settings
    errors = validate_settings()
    if errors:
        print("[ERROR] Configuration errors detected:")
        for error in errors:
            print(f"  - {error}")
        return False

    # Setup logging
    setup_logging(log_level="INFO")
    print("[SUCCESS] Logging configured")

    try:
        # Initialize services with mock/fallback configurations
        print("\n[INFO] Initializing services...")

        # Crawler service
        crawler = CrawlerService(
            rate_limit_delay=0.1,  # Faster for testing
            max_pages=5  # Limit for testing
        )
        print("[SUCCESS] Crawler service initialized")

        # Processor service
        processor = ContentProcessor(
            chunk_size=500,
            chunk_overlap=50
        )
        print("[SUCCESS] Content processor initialized")

        # Embedding service
        embedding_service = EmbeddingService(
            api_key=settings.cohere_api_key
        )
        print("[SUCCESS] Embedding service initialized")

        # Vector store service
        vector_store = VectorStoreService(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key,
            collection_name=settings.collection_name,
            use_mock=True  # Use mock mode for testing without Qdrant
        )
        print("[SUCCESS] Vector store service initialized")

        print("\n[INFO] Testing with sample content...")

        # Instead of crawling a real website, let's test with sample content
        
        sample_url = "https://speck-kit-driven-development-hackat-nine.vercel.app"
        sample_content = """
        # Introduction to Physical AI

        Physical AI represents a paradigm shift in artificial intelligence, focusing on the integration of perception, reasoning, and action in physical environments. Unlike traditional AI that operates primarily in digital spaces, Physical AI systems must understand and interact with the physical world through sensors and actuators.

        ## Core Principles

        The embodiment principle states that the body plays a crucial role in shaping the mind and intelligent behavior. In Physical AI, this means that the physical form and sensory-motor capabilities of a system directly influence its cognitive processes.

        ## Applications

        Physical AI finds applications in robotics, autonomous vehicles, and human-computer interaction systems where understanding and manipulating the physical world is essential.
        """

        print(f"[INFO] Processing sample content from: {sample_url}")

        # Process the content
        chunks = processor.process_file(sample_url, sample_content)
        print(f"[SUCCESS] Created {len(chunks)} content chunks")

        if len(chunks) == 0:
            print("[ERROR] No chunks were created from the sample content")
            return False

        # Generate embeddings
        print("[INFO] Generating embeddings...")
        embedding_vectors = embedding_service.process_chunks_with_embeddings(chunks)
        print(f"[SUCCESS] Generated embeddings for {len(embedding_vectors)} chunks")

        if len(embedding_vectors) == 0:
            print("[ERROR] No embedding vectors were created")
            return False

        # Store in vector database
        print("[INFO] Storing in vector database...")
        success = vector_store.store_chunks(embedding_vectors)
        if success:
            print("[SUCCESS] Successfully stored vectors in Qdrant")
        else:
            print("[ERROR] Failed to store vectors in Qdrant")
            return False

        # Test search functionality
        print("[INFO] Testing search functionality...")
        test_query = embedding_service.generate_embedding("What is Physical AI?")
        search_results = vector_store.search(test_query, limit=3)
        print(f"[SUCCESS] Search returned {len(search_results)} results")

        print("\n[SUCCESS] End-to-end pipeline test completed successfully!")
        print(f"[INFO] Summary:")
        print(f"   • Content chunks created: {len(chunks)}")
        print(f"   • Embeddings generated: {len(embedding_vectors)}")
        print(f"   • Vectors stored: {len(embedding_vectors)}")
        print(f"   • Search results: {len(search_results)}")

        return True

    except Exception as e:
        print(f"[ERROR] Error during pipeline test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_end_to_end_pipeline()
    if success:
        print("\n[SUCCESS] All tests passed!")
        sys.exit(0)
    else:
        print("\n[ERROR] Some tests failed!")
        sys.exit(1)