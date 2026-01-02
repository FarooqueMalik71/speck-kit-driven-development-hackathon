from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class ContentChunk:
    """
    Represents a piece of text content extracted from a web page, processed, and prepared for embedding generation.
    """
    id: str  # unique identifier, generated as hash of source + content + sequence
    content: str  # clean, extracted text content
    source_url: str  # original URL where content was found
    section_title: str  # title or heading associated with the content
    chunk_index: int  # sequence number within the source document
    embedding: Optional[List[float]] = None  # vector representation of the content, optional until generated
    metadata: Dict = field(default_factory=dict)  # additional information like creation timestamp, source file hash
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None

    def __post_init__(self):
        """
        Validate the ContentChunk after initialization
        """
        if not self.id:
            raise ValueError("ContentChunk.id must be provided")
        if not self.content:
            raise ValueError("ContentChunk.content cannot be empty")
        if not self.source_url:
            raise ValueError("ContentChunk.source_url must be provided")
        if self.chunk_index < 0:
            raise ValueError("ContentChunk.chunk_index must be non-negative")
        if self.embedding and len(self.embedding) == 0:
            raise ValueError("ContentChunk.embedding cannot be an empty list")

    @classmethod
    def generate_id(cls, source_url: str, content: str, chunk_index: int) -> str:
        """
        Generate a unique ID for a content chunk based on source URL, content, and chunk index
        """
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        id_source = f"{source_url}_{content_hash}_{chunk_index}"
        return hashlib.sha256(id_source.encode()).hexdigest()


@dataclass
class ContentChunkWithEmbedding(ContentChunk):
    """
    A ContentChunk that is guaranteed to have an embedding
    """
    embedding: List[float]  # vector representation of the content

    def __post_init__(self):
        """
        Validate the ContentChunkWithEmbedding after initialization
        """
        super().__post_init__()
        if not self.embedding:
            raise ValueError("ContentChunkWithEmbedding.embedding must be provided and non-empty")


if __name__ == "__main__":
    # Example usage
    chunk = ContentChunk(
        id=ContentChunk.generate_id("https://example.com/page", "This is sample content", 0),
        content="This is sample content",
        source_url="https://example.com/page",
        section_title="Sample Section",
        chunk_index=0,
        metadata={"word_count": 5, "char_count": 24}
    )

    print("ContentChunk created successfully:")
    print(f"  ID: {chunk.id}")
    print(f"  Content: {chunk.content}")
    print(f"  Source URL: {chunk.source_url}")
    print(f"  Section Title: {chunk.section_title}")
    print(f"  Chunk Index: {chunk.chunk_index}")
    print(f"  Metadata: {chunk.metadata}")
    print(f"  Created At: {chunk.created_at}")