from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class EmbeddingVector:
    """
    Represents a vectorized content chunk stored in Qdrant Cloud with associated metadata.
    """
    id: str  # Qdrant-specific ID, matches ContentChunk.id
    vector: List[float]  # the embedding vector values
    payload: Dict[str, Any]  # metadata stored with the vector in Qdrant
    collection_name: str  # Qdrant collection where vector is stored
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """
        Validate the EmbeddingVector after initialization
        """
        if not self.id:
            raise ValueError("EmbeddingVector.id must be provided")
        if not self.vector:
            raise ValueError("EmbeddingVector.vector must be provided and non-empty")
        if len(self.vector) == 0:
            raise ValueError("EmbeddingVector.vector cannot be an empty list")
        if not self.payload:
            raise ValueError("EmbeddingVector.payload must be provided")
        if not self.collection_name:
            raise ValueError("EmbeddingVector.collection_name must be provided")

        # Validate payload contains required fields
        required_payload_fields = ["content", "source_url", "section_title", "chunk_index", "created_at"]
        for field_name in required_payload_fields:
            if field_name not in self.payload:
                raise ValueError(f"EmbeddingVector.payload must contain '{field_name}' field")

    @classmethod
    def from_content_chunk(cls, chunk_id: str, vector: List[float], content: str, source_url: str,
                          section_title: str, chunk_index: int, collection_name: str = "textbook_content") -> 'EmbeddingVector':
        """
        Create an EmbeddingVector from a ContentChunk
        """
        payload = {
            "content": content,
            "source_url": source_url,
            "section_title": section_title,
            "chunk_index": chunk_index,
            "created_at": datetime.now().isoformat(),
            "chunk_id": chunk_id
        }

        return cls(
            id=chunk_id,
            vector=vector,
            payload=payload,
            collection_name=collection_name
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation
        """
        return {
            "id": self.id,
            "vector": self.vector,
            "payload": self.payload,
            "collection_name": self.collection_name,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmbeddingVector':
        """
        Create from dictionary representation
        """
        return cls(
            id=data["id"],
            vector=data["vector"],
            payload=data["payload"],
            collection_name=data["collection_name"],
            created_at=datetime.fromisoformat(data["created_at"])
        )


@dataclass
class VectorSearchResult:
    """
    Represents a result from a vector search
    """
    id: str
    content: str
    source_url: str
    section_title: str
    score: float  # similarity score
    chunk_index: int
    metadata: Dict[str, Any]

    @classmethod
    def from_payload(cls, payload: Dict[str, Any], score: float) -> 'VectorSearchResult':
        """
        Create from Qdrant search result payload
        """
        return cls(
            id=payload.get("chunk_id", ""),
            content=payload.get("content", ""),
            source_url=payload.get("source_url", ""),
            section_title=payload.get("section_title", ""),
            score=score,
            chunk_index=payload.get("chunk_index", 0),
            metadata={k: v for k, v in payload.items() if k not in ["content", "source_url", "section_title", "chunk_index"]}
        )


@dataclass
class VectorStoreStats:
    """
    Statistics for vector storage operations
    """
    total_vectors: int
    vectors_added: int
    vectors_updated: int
    vectors_deleted: int
    collection_size: int


if __name__ == "__main__":
    # Example usage
    vector = EmbeddingVector.from_content_chunk(
        chunk_id="test-chunk-id-123",
        vector=[0.1, 0.2, 0.3, 0.4, 0.5],
        content="This is sample content for embedding",
        source_url="https://example.com/page",
        section_title="Sample Section",
        chunk_index=0,
        collection_name="textbook_content"
    )

    print("EmbeddingVector created successfully:")
    print(f"  ID: {vector.id}")
    print(f"  Vector length: {len(vector.vector)}")
    print(f"  Collection: {vector.collection_name}")
    print(f"  Payload keys: {list(vector.payload.keys())}")

    # Convert to dict and back
    vector_dict = vector.to_dict()
    restored_vector = EmbeddingVector.from_dict(vector_dict)
    print(f"  Restored vector ID: {restored_vector.id}")