from typing import List, Optional
import logging
from ..models.content_chunk import ContentChunk
from ..models.embedding_vector import EmbeddingVector

logger = logging.getLogger(__name__)

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    logger.warning("Cohere library not available. Using mock implementation.")
    COHERE_AVAILABLE = False


class EmbeddingService:
    """
    Service for generating vector embeddings using Cohere API
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "embed-multilingual-v3.0"):
        import os
        self.model = model
        self.client = None
        api_key = api_key or os.getenv("COHERE_API_KEY")

        if COHERE_AVAILABLE and api_key:
            try:
                self.client = cohere.Client(api_key)
                logger.info(f"Successfully initialized Cohere client with model: {model}")
            except Exception as e:
                logger.error(f"Failed to initialize Cohere client: {str(e)}")
                self.client = None
        else:
            logger.warning("Cohere client not initialized. Using mock implementation for testing.")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        """
        if self.client:
            try:
                response = self.client.embed(
                    texts=[text],
                    model=self.model,
                    input_type="search_document"
                )
                return response.embeddings[0]
            except Exception as e:
                logger.error(f"Error generating embedding: {str(e)}")
                raise
        else:
            raise RuntimeError("Cohere client not initialized. Set COHERE_API_KEY environment variable.")

    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 96) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts
        Cohere's free tier has limits, so we process in smaller batches
        """
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                if self.client:
                    response = self.client.embed(
                        texts=batch,
                        model=self.model,
                        input_type="search_document"
                    )
                    batch_embeddings = response.embeddings
                else:
                    raise RuntimeError("Cohere client not initialized. Set COHERE_API_KEY environment variable.")

                all_embeddings.extend(batch_embeddings)
                logger.debug(f"Generated embeddings for batch {i//batch_size + 1}: {len(batch)} items")

            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i//batch_size + 1}: {str(e)}")
                # Fallback: generate embeddings one by one for the failed batch
                for text in batch:
                    all_embeddings.append(self.generate_embedding(text))

        return all_embeddings

    def process_chunks_with_embeddings(self, chunks: List[ContentChunk]) -> List[EmbeddingVector]:
        """
        Process content chunks and generate embeddings for them
        """
        logger.info(f"Generating embeddings for {len(chunks)} content chunks")

        if not chunks:
            return []

        # Extract text content from chunks
        texts = [chunk.content for chunk in chunks]

        # Generate embeddings in batch
        embeddings = self.generate_embeddings_batch(texts)

        # Create EmbeddingVector objects with the embeddings
        embedding_vectors = []
        for chunk, embedding in zip(chunks, embeddings):
            embedding_vector = EmbeddingVector.from_content_chunk(
                chunk_id=chunk.id,
                vector=embedding,
                content=chunk.content,
                source_url=chunk.source_url,
                section_title=chunk.section_title,
                chunk_index=chunk.chunk_index
            )
            embedding_vectors.append(embedding_vector)

        logger.info(f"Successfully created {len(embedding_vectors)} embedding vectors with embeddings")
        return embedding_vectors

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings for the current model
        """
        # For Cohere's embed-multilingual-v3.0, the default output dimension is 1024
        # but it can vary based on the input_type parameter
        # For search_document, it's typically 1024
        if self.client:
            # We could make a test call to determine the actual dimension
            test_embedding = self.generate_embedding("test")
            return len(test_embedding)
        else:
            # Default dimension for Cohere models
            return 1024

    def validate_embedding(self, embedding: List[float]) -> bool:
        """
        Validate that an embedding is properly formed
        """
        if not embedding:
            return False

        # Check that all values are numbers
        if not all(isinstance(x, (int, float)) for x in embedding):
            return False

        # Check for reasonable range (embeddings are typically normalized)
        if any(abs(x) > 1000 for x in embedding):
            logger.warning("Embedding contains unusually large values")

        return True


if __name__ == "__main__":
    # Example usage
    import os
    api_key = os.getenv("COHERE_API_KEY")  # Use actual key from environment for testing

    if api_key:
        service = EmbeddingService(api_key=api_key)
        print("Embedding service initialized with Cohere client")
    else:
        service = EmbeddingService()  # Will use mock
        print("Embedding service initialized with mock client")

    # Example content chunks
    from models.content_chunk import ContentChunk
    import hashlib
    from datetime import datetime

    test_content = "Physical AI represents a paradigm shift in artificial intelligence, focusing on the integration of perception, reasoning, and action in physical environments."
    content_hash = hashlib.sha256(test_content.encode()).hexdigest()

    chunk = ContentChunk(
        id=f"test_{content_hash}_0",
        content=test_content,
        source_url="https://example.com/test",
        section_title="Introduction",
        chunk_index=0,
        created_at=datetime.now()
    )

    # Generate embedding for the chunk
    embedding = service.generate_embedding(chunk.content)
    print(f"Generated embedding with {len(embedding)} dimensions")
    print(f"First 5 values: {embedding[:5]}")

    # Process chunks with embeddings
    chunks_with_embeddings = service.process_chunks_with_embeddings([chunk])
    print(f"Created {len(chunks_with_embeddings)} embedding vectors")

    # Check embedding dimension
    dim = service.get_embedding_dimension()
    print(f"Embedding dimension: {dim}")