from typing import List, Optional
import logging
from openai import OpenAI
from ..config import settings
from .content_processor import ContentChunk

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating vector embeddings using OpenAI API"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding of length {len(embedding)} for text of length {len(text)}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model
                )

                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)

                logger.debug(f"Generated {len(batch_embeddings)} embeddings in batch {i//batch_size + 1}")

            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i//batch_size + 1}: {str(e)}")
                # Generate embeddings one by one for the failed batch
                for text in batch:
                    all_embeddings.append(self.generate_embedding(text))

        return all_embeddings

    def process_chunks_with_embeddings(self, chunks: List[ContentChunk]) -> List[ContentChunk]:
        """Process content chunks and add embeddings to them"""
        logger.info(f"Generating embeddings for {len(chunks)} chunks")

        if not chunks:
            return chunks

        # Extract text content from chunks
        texts = [chunk.content for chunk in chunks]

        # Generate embeddings in batch
        embeddings = self.generate_embeddings_batch(texts)

        # Assign embeddings back to chunks
        processed_chunks = []
        for chunk, embedding in zip(chunks, embeddings):
            chunk_with_embedding = ContentChunk(
                id=chunk.id,
                content=chunk.content,
                metadata=chunk.metadata,
                source_file=chunk.source_file,
                chunk_index=chunk.chunk_index,
                embedding=embedding
            )
            processed_chunks.append(chunk_with_embedding)

        logger.info(f"Successfully processed {len(processed_chunks)} chunks with embeddings")
        return processed_chunks

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings for the current model"""
        # Generate a test embedding to determine dimensions
        test_embedding = self.generate_embedding("test")
        return len(test_embedding)

# Example usage
if __name__ == "__main__":
    from .content_processor import ContentProcessor

    # Initialize services
    processor = ContentProcessor()
    embedding_service = EmbeddingService()

    # Sample content
    sample_content = """
    # Introduction to Physical AI

    Physical AI represents a paradigm shift in artificial intelligence, focusing on the integration of perception, reasoning, and action in physical environments. Unlike traditional AI that operates primarily in digital spaces, Physical AI systems must understand and interact with the physical world through sensors and actuators.
    """

    # Process content into chunks
    chunks = processor.process_file("sample.md", sample_content)

    # Generate embeddings for chunks
    chunks_with_embeddings = embedding_service.process_chunks_with_embeddings(chunks)

    print(f"Generated embeddings for {len(chunks_with_embeddings)} chunks")
    print(f"Embedding dimension: {embedding_service.get_embedding_dimension()}")
    print(f"First chunk embedding preview: {chunks_with_embeddings[0].embedding[:10]}...")