from typing import List, Dict, Any, Optional
import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
from config import settings
from models.embedding_vector import EmbeddingVector

logger = logging.getLogger(__name__)

class VectorStoreService:
    """Service for storing and retrieving vector embeddings in Qdrant"""

    def __init__(self, host: str = None, port: int = None, api_key: str = None, collection_name: str = "textbook_content", use_mock: bool = False):
        self.collection_name = collection_name
        self.use_mock = use_mock

        if use_mock:
            # Use mock mode for testing without actual Qdrant connection
            logger.info("VectorStoreService initialized in mock mode for testing")
            self.client = None
        else:
            # Use provided values or fallback to settings
            host = host or settings.qdrant_host
            port = port or settings.qdrant_port
            api_key = api_key or settings.qdrant_api_key

            try:
                # Handle local vs cloud Qdrant connections
                if host == "localhost" or host.startswith("127.0.0.1"):
                    # For local Qdrant, use host and port
                    self.client = QdrantClient(
                        host=host,
                        port=port,
                        prefer_grpc=False,  # Use HTTP for local connections
                    )
                else:
                    # For cloud Qdrant, use URL (without protocol) and API key with HTTPS
                    # Remove protocol prefix if present for proper URL handling
                    clean_host = host.replace("https://", "").replace("http://", "")
                    self.client = QdrantClient(
                        url=clean_host,
                        port=port,
                        api_key=api_key,
                        https=True,  # Enable HTTPS for cloud connections
                        prefer_grpc=True,
                        # Disable compatibility check to avoid the warning
                        check_compatibility=False
                    )

                # Test the connection by trying to get collections
                try:
                    self.client.get_collections()
                    logger.info("Successfully connected to Qdrant")
                    self._ensure_collection_exists()
                except Exception as conn_error:
                    logger.warning(f"Could not connect to Qdrant: {conn_error}. Switching to mock mode.")
                    self.use_mock = True
                    self.client = None

            except Exception as e:
                logger.error(f"Failed to initialize Qdrant client: {str(e)}. Using mock mode.")
                self.use_mock = True
                self.client = None

    def _ensure_collection_exists(self):
        """Ensure the collection exists with proper configuration"""
        if self.use_mock:
            # Skip collection creation in mock mode
            return

        try:
            # Try to get collection info
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' already exists")
        except Exception as e:
            logger.warning(f"Collection '{self.collection_name}' does not exist or connection error: {str(e)}")
            # Create collection if it doesn't exist
            # Default to Cohere's embedding dimension (1024 for most models)
            # In a real implementation, we'd get this from the embedding service
            vector_size = 1024

            try:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Created collection '{self.collection_name}' with {vector_size} dimensional vectors")
            except Exception as create_error:
                logger.error(f"Failed to create collection '{self.collection_name}': {str(create_error)}")
                # In case of failure to connect, we can still continue with operations
                # but warn the user that vector storage may not work
                raise create_error

    def store_chunks(self, embedding_vectors: List[EmbeddingVector], batch_size: int = 64) -> bool:
        """Store embedding vectors in vector store with idempotent behavior"""
        logger.info(f"Storing {len(embedding_vectors)} embedding vectors in vector store")

        if self.use_mock:
            # Mock implementation for testing
            logger.info(f"[MOCK] Would store {len(embedding_vectors)} embedding vectors in vector store")
            return True

        try:
            # Check if client is available
            if not self.client:
                logger.error("Qdrant client not available")
                return False

            points = []
            for emb_vector in embedding_vectors:
                # Prepare payload with content and metadata
                payload = {
                    "content": emb_vector.payload.get("content", ""),
                    "source_url": emb_vector.payload.get("source_url", ""),
                    "section_title": emb_vector.payload.get("section_title", ""),
                    "chunk_index": emb_vector.payload.get("chunk_index", 0),
                    "created_at": emb_vector.payload.get("created_at", ""),
                    "chunk_id": emb_vector.payload.get("chunk_id", emb_vector.id)
                }

                # Add any additional metadata from the original payload
                for key, value in emb_vector.payload.items():
                    if key not in payload:
                        payload[key] = value

                # Create point structure
                point = PointStruct(
                    id=emb_vector.id,
                    vector=emb_vector.vector,
                    payload=payload
                )
                points.append(point)

                # Batch insert when we reach batch_size
                if len(points) >= batch_size:
                    # Use upsert to ensure idempotent behavior (update if exists, create if not)
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=points
                    )
                    logger.debug(f"Upserted batch of {len(points)} points")
                    points = []

            # Insert remaining points
            if points:
                # Use upsert to ensure idempotent behavior (update if exists, create if not)
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                logger.debug(f"Upserted final batch of {len(points)} points")

            logger.info(f"Successfully stored {len(embedding_vectors)} embedding vectors in vector store")
            return True

        except Exception as e:
            logger.error(f"Error storing embedding vectors in vector store: {str(e)}")
            return False

    def idempotent_store_chunks(self, embedding_vectors: List[EmbeddingVector], batch_size: int = 64) -> bool:
        """Store embedding vectors with explicit idempotent behavior by checking for existence first"""
        logger.info(f"Idempotently storing {len(embedding_vectors)} embedding vectors in vector store")

        if self.use_mock:
            # Mock implementation for testing
            logger.info(f"[MOCK] Would idempotently store {len(embedding_vectors)} embedding vectors in vector store")
            return True

        try:
            # Check if client is available
            if not self.client:
                logger.error("Qdrant client not available")
                return False

            # First, identify which vectors already exist in the collection
            existing_ids = set()
            for emb_vector in embedding_vectors:
                try:
                    # Try to retrieve the vector by ID to see if it exists
                    existing_points = self.client.retrieve(
                        collection_name=self.collection_name,
                        ids=[emb_vector.id],
                        with_payload=False,
                        with_vectors=False
                    )
                    if existing_points:
                        existing_ids.add(emb_vector.id)
                except Exception:
                    # If retrieval fails, assume it doesn't exist
                    pass

            # Only store vectors that don't already exist
            new_vectors = [ev for ev in embedding_vectors if ev.id not in existing_ids]

            if new_vectors:
                logger.info(f"Found {len(existing_ids)} existing vectors, storing {len(new_vectors)} new vectors")

                # Store the new vectors
                points = []
                for emb_vector in new_vectors:
                    # Prepare payload with content and metadata
                    payload = {
                        "content": emb_vector.payload.get("content", ""),
                        "source_url": emb_vector.payload.get("source_url", ""),
                        "section_title": emb_vector.payload.get("section_title", ""),
                        "chunk_index": emb_vector.payload.get("chunk_index", 0),
                        "created_at": emb_vector.payload.get("created_at", ""),
                        "chunk_id": emb_vector.payload.get("chunk_id", emb_vector.id)
                    }

                    # Add any additional metadata from the original payload
                    for key, value in emb_vector.payload.items():
                        if key not in payload:
                            payload[key] = value

                    # Create point structure
                    point = PointStruct(
                        id=emb_vector.id,
                        vector=emb_vector.vector,
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

                logger.info(f"Successfully stored {len(new_vectors)} new embedding vectors in vector store")
            else:
                logger.info("All vectors already exist in the vector store, no new vectors to store")

            return True

        except Exception as e:
            logger.error(f"Error in idempotent storage: {str(e)}")
            return False

    def search(self, query_embedding: List[float], limit: int = 10, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar content using vector similarity"""
        if self.use_mock:
            # Mock implementation for testing - return empty results
            logger.info(f"[MOCK] Would search for similar content, returning empty results for testing")
            return []

        try:
            # Check if client is available
            if not self.client:
                logger.error("Qdrant client not available")
                return []

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

            # Perform search - use query_points for this Qdrant version
            search_results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=limit,
                with_payload=True,
                with_vectors=False,
                query_filter=qdrant_filters
            )

            results = []
            # Handle different response formats depending on Qdrant version
            # For query_points, the results are in search_results.points
            search_points = search_results.points if hasattr(search_results, 'points') else search_results

            for hit in search_points:
                # Handle different object structures
                point_id = getattr(hit, 'id', getattr(hit, 'payload', {}).get('id', 'unknown'))
                payload = getattr(hit, 'payload', {})
                score = getattr(hit, 'score', 0.0)

                result = {
                    "id": point_id,
                    "content": payload.get("content", "") if isinstance(payload, dict) else getattr(hit, 'payload', {}).get("content", ""),
                    "source_url": payload.get("source_url", "") if isinstance(payload, dict) else getattr(hit, 'payload', {}).get("source_url", ""),
                    "section_title": payload.get("section_title", "") if isinstance(payload, dict) else getattr(hit, 'payload', {}).get("section_title", ""),
                    "chunk_index": payload.get("chunk_index", 0) if isinstance(payload, dict) else getattr(hit, 'payload', {}).get("chunk_index", 0),
                    "created_at": payload.get("created_at", "") if isinstance(payload, dict) else getattr(hit, 'payload', {}).get("created_at", ""),
                    "chunk_id": payload.get("chunk_id", "") if isinstance(payload, dict) else getattr(hit, 'payload', {}).get("chunk_id", ""),
                    "metadata": {},
                    "score": score
                }

                # Add metadata - handle different payload structures
                if isinstance(payload, dict):
                    result["metadata"] = {k: v for k, v in payload.items()
                                        if k not in ["content", "source_url", "section_title", "chunk_index", "created_at", "chunk_id"]}
                else:
                    # If payload is an object, try to extract its attributes
                    payload_attrs = getattr(hit, 'payload', {})
                    if isinstance(payload_attrs, dict):
                        result["metadata"] = {k: v for k, v in payload_attrs.items()
                                            if k not in ["content", "source_url", "section_title", "chunk_index", "created_at", "chunk_id"]}

                results.append(result)

            logger.debug(f"Search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []

    def search_with_content_filter(self, query_embedding: List[float], content_filter: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search with specific content filtering"""
        if self.use_mock:
            # Mock implementation for testing - return empty results
            logger.info(f"[MOCK] Would search with content filter, returning empty results for testing")
            return []

        try:
            # Check if client is available
            if not self.client:
                logger.error("Qdrant client not available")
                return []

            # Filter based on content or metadata
            filter_condition = models.Filter(
                must=[
                    models.FieldCondition(
                        key="content",
                        match=models.MatchText(text=content_filter)
                    )
                ]
            )

            search_results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=limit,
                with_payload=True,
                with_vectors=False,
                query_filter=filter_condition
            )

            results = []
            # Handle different response formats depending on Qdrant version
            # For query_points, the results are in search_results.points
            search_points = search_results.points if hasattr(search_results, 'points') else search_results

            for hit in search_points:
                # Handle different object structures
                point_id = getattr(hit, 'id', getattr(hit, 'payload', {}).get('id', 'unknown'))
                payload = getattr(hit, 'payload', {})
                score = getattr(hit, 'score', 0.0)

                result = {
                    "id": point_id,
                    "content": payload.get("content", "") if isinstance(payload, dict) else getattr(hit, 'payload', {}).get("content", ""),
                    "source_url": payload.get("source_url", "") if isinstance(payload, dict) else getattr(hit, 'payload', {}).get("source_url", ""),
                    "section_title": payload.get("section_title", "") if isinstance(payload, dict) else getattr(hit, 'payload', {}).get("section_title", ""),
                    "chunk_index": payload.get("chunk_index", 0) if isinstance(payload, dict) else getattr(hit, 'payload', {}).get("chunk_index", 0),
                    "created_at": payload.get("created_at", "") if isinstance(payload, dict) else getattr(hit, 'payload', {}).get("created_at", ""),
                    "chunk_id": payload.get("chunk_id", "") if isinstance(payload, dict) else getattr(hit, 'payload', {}).get("chunk_id", ""),
                    "metadata": {},
                    "score": score
                }

                # Add metadata - handle different payload structures
                if isinstance(payload, dict):
                    result["metadata"] = {k: v for k, v in payload.items()
                                        if k not in ["content", "source_url", "section_title", "chunk_index", "created_at", "chunk_id"]}
                else:
                    # If payload is an object, try to extract its attributes
                    payload_attrs = getattr(hit, 'payload', {})
                    if isinstance(payload_attrs, dict):
                        result["metadata"] = {k: v for k, v in payload_attrs.items()
                                            if k not in ["content", "source_url", "section_title", "chunk_index", "created_at", "chunk_id"]}

                results.append(result)

            logger.debug(f"Filtered search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error in filtered search: {str(e)}")
            return []

    def delete_by_source_url(self, source_url: str) -> bool:
        """Delete all chunks associated with a specific source URL"""
        if self.use_mock:
            # Mock implementation for testing
            logger.info(f"[MOCK] Would delete chunks for source URL: {source_url}")
            return True

        try:
            # Check if client is available
            if not self.client:
                logger.error("Qdrant client not available")
                return False

            # Find points with matching source URL
            scroll_results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="source_url",
                            match=models.MatchValue(value=source_url)
                        )
                    ]
                ),
                limit=10000  # Adjust based on expected max chunks per URL
            )

            point_ids = [point.id for point in scroll_results[0]]

            if point_ids:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(
                        points=point_ids
                    )
                )
                logger.info(f"Deleted {len(point_ids)} chunks for source URL {source_url}")

            return True

        except Exception as e:
            logger.error(f"Error deleting chunks for source URL {source_url}: {str(e)}")
            return False

    def get_content_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific content chunk by ID"""
        if self.use_mock:
            # Mock implementation for testing - return None
            logger.info(f"[MOCK] Would retrieve content by ID: {chunk_id}")
            return None

        try:
            # Check if client is available
            if not self.client:
                logger.error("Qdrant client not available")
                return None

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
                    "content": point.payload.get("content", ""),
                    "source_url": point.payload.get("source_url", ""),
                    "section_title": point.payload.get("section_title", ""),
                    "chunk_index": point.payload.get("chunk_index", 0),
                    "created_at": point.payload.get("created_at", ""),
                    "chunk_id": point.payload.get("chunk_id", ""),
                    "metadata": {k: v for k, v in point.payload.items()
                                if k not in ["content", "source_url", "section_title", "chunk_index", "created_at", "chunk_id"]}
                }

            return None

        except Exception as e:
            logger.error(f"Error retrieving content by ID {chunk_id}: {str(e)}")
            return None

    def get_all_collections(self) -> List[str]:
        """Get list of all collections in the vector store"""
        if self.use_mock:
            # Mock implementation for testing - return empty list
            logger.info("[MOCK] Would get all collections, returning empty list for testing")
            return []

        try:
            # Check if client is available
            if not self.client:
                logger.error("Qdrant client not available")
                return []

            collections = self.client.get_collections()
            return [collection.name for collection in collections.collections]
        except Exception as e:
            logger.error(f"Error getting collections: {str(e)}")
            return []

    def clear_collection(self) -> bool:
        """Clear all data from the collection (use with caution!)"""
        if self.use_mock:
            # Mock implementation for testing
            logger.info(f"[MOCK] Would clear collection '{self.collection_name}'")
            return True

        try:
            # Check if client is available
            if not self.client:
                logger.error("Qdrant client not available")
                return False

            self.client.delete_collection(self.collection_name)
            self._ensure_collection_exists()
            logger.info(f"Cleared and recreated collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    from models.content_chunk import ContentChunk
    from .embedding_service import EmbeddingService
    import hashlib
    from datetime import datetime

    # Initialize services
    embedding_service = EmbeddingService()
    vector_store = VectorStoreService()

    # Sample content
    sample_content = """
    # Introduction to Physical AI

    Physical AI represents a paradigm shift in artificial intelligence, focusing on the integration of perception, reasoning, and action in physical environments. Unlike traditional AI that operates primarily in digital spaces, Physical AI systems must understand and interact with the physical world through sensors and actuators.
    """

    # Create a sample ContentChunk
    content_hash = hashlib.sha256(sample_content.encode()).hexdigest()
    chunk = ContentChunk(
        id=f"test_{content_hash}_0",
        content=sample_content,
        source_url="https://example.com/test",
        section_title="Introduction",
        chunk_index=0,
        created_at=datetime.now()
    )

    # Generate embeddings for the chunk
    embedding_vectors = embedding_service.process_chunks_with_embeddings([chunk])

    # Store in vector store
    success = vector_store.store_chunks(embedding_vectors)
    print(f"Storage success: {success}")

    # Test search
    query_embedding = embedding_service.generate_embedding("What is Physical AI?")
    search_results = vector_store.search(query_embedding, limit=5)
    print(f"Search returned {len(search_results)} results")
    for result in search_results:
        print(f"Score: {result['score']}, Content preview: {result['content'][:100]}...")