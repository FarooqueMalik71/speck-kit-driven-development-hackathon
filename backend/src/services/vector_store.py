from typing import List, Dict, Any, Optional
import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
from ..config import settings
from .content_processor import ContentChunk

logger = logging.getLogger(__name__)

class VectorStoreService:
    """Service for storing and retrieving vector embeddings in Qdrant"""

    def __init__(self, collection_name: str = "textbook_content"):
        self.collection_name = collection_name
        self.client = QdrantClient(
            url=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key,
            prefer_grpc=True
        )
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Ensure the collection exists with proper configuration"""
        try:
            # Try to get collection info
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' already exists")
        except:
            # Create collection if it doesn't exist
            embedding_service = self._get_embedding_service()
            vector_size = embedding_service.get_embedding_dimension()

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created collection '{self.collection_name}' with {vector_size} dimensional vectors")

    def _get_embedding_service(self):
        """Get embedding service instance (helper method)"""
        from .embedding_service import EmbeddingService
        return EmbeddingService()

    def store_chunks(self, chunks: List[ContentChunk], batch_size: int = 64) -> bool:
        """Store content chunks in vector store"""
        logger.info(f"Storing {len(chunks)} chunks in vector store")

        try:
            points = []
            for chunk in chunks:
                # Prepare payload with content and metadata
                payload = {
                    "content": chunk.content,
                    "source_file": chunk.source_file,
                    "chunk_index": chunk.chunk_index,
                    "metadata": chunk.metadata,
                    "id": chunk.id
                }

                # Create point structure
                point = PointStruct(
                    id=chunk.id,
                    vector=chunk.embedding,
                    payload=payload
                )
                points.append(point)

                # Batch insert when we reach batch_size
                if len(points) >= batch_size:
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=points
                    )
                    logger.debug(f"Upserted batch of {len(points)} points")
                    points = []

            # Insert remaining points
            if points:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                logger.debug(f"Upserted final batch of {len(points)} points")

            logger.info(f"Successfully stored {len(chunks)} chunks in vector store")
            return True

        except Exception as e:
            logger.error(f"Error storing chunks in vector store: {str(e)}")
            return False

    def search(self, query_embedding: List[float], limit: int = 10, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar content using vector similarity"""
        try:
            # Prepare filters if provided
            qdrant_filters = None
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    if isinstance(value, str):
                        filter_conditions.append(
                            models.FieldCondition(
                                key=f"metadata.{key}",
                                match=models.MatchValue(value=value)
                            )
                        )
                    elif isinstance(value, list):
                        filter_conditions.append(
                            models.FieldCondition(
                                key=f"metadata.{key}",
                                match=models.MatchAny(any=value)
                            )
                        )

                if filter_conditions:
                    qdrant_filters = models.Filter(must=filter_conditions)

            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                with_payload=True,
                with_vectors=False,
                query_filter=qdrant_filters
            )

            results = []
            for hit in search_results:
                result = {
                    "id": hit.id,
                    "content": hit.payload["content"],
                    "source_file": hit.payload["source_file"],
                    "chunk_index": hit.payload["chunk_index"],
                    "metadata": hit.payload["metadata"],
                    "score": hit.score
                }
                results.append(result)

            logger.debug(f"Search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []

    def search_with_content_filter(self, query_embedding: List[float], content_filter: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search with specific content filtering"""
        try:
            # Filter based on content or metadata
            filter_condition = models.Filter(
                must=[
                    models.FieldCondition(
                        key="content",
                        match=models.MatchText(text=content_filter)
                    )
                ]
            )

            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                with_payload=True,
                with_vectors=False,
                query_filter=filter_condition
            )

            results = []
            for hit in search_results:
                result = {
                    "id": hit.id,
                    "content": hit.payload["content"],
                    "source_file": hit.payload["source_file"],
                    "chunk_index": hit.payload["chunk_index"],
                    "metadata": hit.payload["metadata"],
                    "score": hit.score
                }
                results.append(result)

            logger.debug(f"Filtered search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error in filtered search: {str(e)}")
            return []

    def delete_by_source_file(self, source_file: str) -> bool:
        """Delete all chunks associated with a specific source file"""
        try:
            # Find points with matching source file
            scroll_results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="source_file",
                            match=models.MatchValue(value=source_file)
                        )
                    ]
                ),
                limit=10000  # Adjust based on expected max chunks per file
            )

            point_ids = [point.id for point in scroll_results[0]]

            if point_ids:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(
                        points=point_ids
                    )
                )
                logger.info(f"Deleted {len(point_ids)} chunks for file {source_file}")

            return True

        except Exception as e:
            logger.error(f"Error deleting chunks for file {source_file}: {str(e)}")
            return False

    def get_content_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific content chunk by ID"""
        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[chunk_id],
                with_payload=True,
                with_vectors=False
            )

            if points and len(points) > 0:
                point = points[0]
                return {
                    "id": point.id,
                    "content": point.payload["content"],
                    "source_file": point.payload["source_file"],
                    "chunk_index": point.payload["chunk_index"],
                    "metadata": point.payload["metadata"]
                }

            return None

        except Exception as e:
            logger.error(f"Error retrieving content by ID {chunk_id}: {str(e)}")
            return None

    def get_all_collections(self) -> List[str]:
        """Get list of all collections in the vector store"""
        try:
            collections = self.client.get_collections()
            return [collection.name for collection in collections.collections]
        except Exception as e:
            logger.error(f"Error getting collections: {str(e)}")
            return []

    def clear_collection(self) -> bool:
        """Clear all data from the collection (use with caution!)"""
        try:
            self.client.delete_collection(self.collection_name)
            self._ensure_collection_exists()
            logger.info(f"Cleared and recreated collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    from .content_processor import ContentProcessor
    from .embedding_service import EmbeddingService

    # Initialize services
    processor = ContentProcessor()
    embedding_service = EmbeddingService()
    vector_store = VectorStoreService()

    # Sample content
    sample_content = """
    # Introduction to Physical AI

    Physical AI represents a paradigm shift in artificial intelligence, focusing on the integration of perception, reasoning, and action in physical environments. Unlike traditional AI that operates primarily in digital spaces, Physical AI systems must understand and interact with the physical world through sensors and actuators.
    """

    # Process content into chunks
    chunks = processor.process_file("sample.md", sample_content)

    # Generate embeddings for chunks
    chunks_with_embeddings = embedding_service.process_chunks_with_embeddings(chunks)

    # Store in vector store
    success = vector_store.store_chunks(chunks_with_embeddings)
    print(f"Storage success: {success}")

    # Test search
    query_embedding = embedding_service.generate_embedding("What is Physical AI?")
    search_results = vector_store.search(query_embedding, limit=5)
    print(f"Search returned {len(search_results)} results")
    for result in search_results:
        print(f"Score: {result['score']}, Content preview: {result['content'][:100]}...")