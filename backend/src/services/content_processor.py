from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime
import hashlib
from dataclasses import dataclass
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import re

logger = logging.getLogger(__name__)

@dataclass
class ContentChunk:
    """Represents a chunk of content for embedding"""
    id: str
    content: str
    metadata: Dict[str, Any]
    source_file: str
    chunk_index: int
    embedding: Optional[List[float]] = None

class ContentProcessor:
    """Processes textbook content for vector embedding"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def extract_metadata_from_filename(self, filepath: str) -> Dict[str, Any]:
        """Extract metadata from file path and name"""
        path = Path(filepath)
        return {
            'filename': path.name,
            'filepath': str(path),
            'directory': str(path.parent),
            'extension': path.suffix,
            'created_at': datetime.fromtimestamp(path.stat().st_ctime).isoformat(),
            'updated_at': datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
        }

    def clean_content(self, content: str) -> str:
        """Clean and normalize content"""
        # Remove multiple consecutive newlines
        content = re.sub(r'\n\s*\n', '\n\n', content)

        # Remove extra whitespace
        content = re.sub(r'[ \t]+', ' ', content)

        # Remove markdown artifacts that shouldn't be in embeddings
        content = re.sub(r'\{#[^}]+\}', '', content)  # Remove anchor links
        content = re.sub(r'<.*?>', '', content)  # Remove HTML tags
        content = re.sub(r'```.+?```', '', content, flags=re.DOTALL)  # Remove code blocks

        return content.strip()

    def extract_content_from_markdown(self, content: str) -> str:
        """Extract only the meaningful text from markdown"""
        # Remove markdown headers but preserve the text
        content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)

        # Remove markdown bold/italic markers
        content = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', content)
        content = re.sub(r'_{1,2}([^_]+)_{1,2}', r'\1', content)

        # Remove markdown links but preserve the text [text](url) -> text
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)

        # Remove markdown images
        content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', content)

        # Remove markdown code spans
        content = re.sub(r'`([^`]+)`', r'\1', content)

        # Remove horizontal rules
        content = re.sub(r'^\s*[-*_]{3,}\s*$', '', content, flags=re.MULTILINE)

        return content

    def process_file(self, filepath: str, content: str) -> List[ContentChunk]:
        """Process a single file into content chunks"""
        logger.info(f"Processing file: {filepath}")

        # Extract and enhance metadata
        metadata = self.extract_metadata_from_filename(filepath)
        metadata['file_hash'] = hashlib.md5(content.encode()).hexdigest()
        metadata['word_count'] = len(content.split())
        metadata['char_count'] = len(content)

        # Clean and extract meaningful content
        cleaned_content = self.clean_content(content)
        markdown_content = self.extract_content_from_markdown(cleaned_content)

        # Create LangChain documents for splitting
        doc = Document(page_content=markdown_content, metadata=metadata)

        # Split into chunks
        split_docs = self.text_splitter.split_documents([doc])

        chunks = []
        for i, split_doc in enumerate(split_docs):
            chunk_id = f"{metadata['file_hash']}_{i}"

            chunk = ContentChunk(
                id=chunk_id,
                content=split_doc.page_content,
                metadata=split_doc.metadata,
                source_file=filepath,
                chunk_index=i
            )
            chunks.append(chunk)

            logger.debug(f"Created chunk {i} for {filepath}: {len(split_doc.page_content)} chars")

        logger.info(f"Created {len(chunks)} chunks from {filepath}")
        return chunks

    def process_directory(self, directory: str, file_extensions: List[str] = ['.md', '.txt']) -> List[ContentChunk]:
        """Process all files in a directory"""
        all_chunks = []

        dir_path = Path(directory)
        for ext in file_extensions:
            for file_path in dir_path.rglob(f"*{ext}"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    chunks = self.process_file(str(file_path), content)
                    all_chunks.extend(chunks)

                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    continue

        logger.info(f"Processed directory {directory}, created {len(all_chunks)} total chunks")
        return all_chunks

# Example usage
if __name__ == "__main__":
    processor = ContentProcessor()

    # Example of processing a single file
    sample_content = """
    # Introduction to Physical AI

    Physical AI represents a paradigm shift in artificial intelligence, focusing on the integration of perception, reasoning, and action in physical environments. Unlike traditional AI that operates primarily in digital spaces, Physical AI systems must understand and interact with the physical world through sensors and actuators.

    ## Core Principles

    The embodiment principle states that the body plays a crucial role in shaping the mind and intelligent behavior. In Physical AI, this means that the physical form and sensory-motor capabilities of a system directly influence its cognitive processes.
    """

    chunks = processor.process_file("sample.md", sample_content)
    for chunk in chunks:
        print(f"Chunk {chunk.chunk_index}: {len(chunk.content)} chars")
        print(f"Content preview: {chunk.content[:100]}...")
        print("---")