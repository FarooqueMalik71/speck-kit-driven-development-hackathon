from typing import List, Dict, Any, Optional, Tuple
import logging
import re
from dataclasses import dataclass
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter
from .content_processor import ContentChunk

logger = logging.getLogger(__name__)

@dataclass
class ChunkingConfig:
    """Configuration for content chunking"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    separators: List[str] = None
    length_function: callable = len

    def __post_init__(self):
        if self.separators is None:
            # Default separators ordered by preference
            self.separators = [
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                " ",     # Spaces
                ""       # Character level (last resort)
            ]

class ChunkingService:
    """Service for advanced content chunking with multiple strategies"""

    def __init__(self, config: ChunkingConfig = None):
        self.config = config or ChunkingConfig()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            length_function=self.config.length_function,
            is_separator_regex=False,
            separators=self.config.separators
        )
        self.markdown_splitter = MarkdownTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            length_function=self.config.length_function
        )

    def chunk_by_semantic_boundaries(self, content: str, source_file: str) -> List[ContentChunk]:
        """Chunk content based on semantic boundaries like headers, sections, etc."""
        chunks = []

        # Split by markdown headers first
        header_pattern = r'^(#{1,6})\s+(.+)$'
        header_matches = list(re.finditer(header_pattern, content, re.MULTILINE))

        if header_matches:
            # Process content in sections between headers
            start = 0
            for match in header_matches:
                # Add content before this header
                if match.start() > start:
                    section_content = content[start:match.start()]
                    section_chunks = self._chunk_section(section_content, source_file, f"section_{start}")
                    chunks.extend(section_chunks)

                # Add the header as its own chunk (or combine with next content)
                header_end = content.find('\n', match.end())
                if header_end != -1:
                    header_content = content[match.start():header_end+1]
                    # Combine header with following content
                    next_section_end = self._find_next_header(content, header_end)
                    combined_content = content[match.start():next_section_end]
                    header_chunks = self._chunk_section(combined_content, source_file, f"header_{match.start()}")
                    chunks.extend(header_chunks)
                    start = next_section_end
                else:
                    start = match.end()

            # Add remaining content after last header
            if start < len(content):
                remaining_chunks = self._chunk_section(content[start:], source_file, f"remaining_{start}")
                chunks.extend(remaining_chunks)
        else:
            # If no headers, use regular splitting
            chunks = self._chunk_section(content, source_file, "content")

        return chunks

    def _find_next_header(self, content: str, start_pos: int) -> int:
        """Find the position of the next header after start_pos"""
        header_pattern = r'^(#{1,6})\s+(.+)$'
        remaining_content = content[start_pos:]
        match = re.search(header_pattern, remaining_content, re.MULTILINE)
        if match:
            return start_pos + match.start()
        return len(content)

    def _chunk_section(self, content: str, source_file: str, section_id: str) -> List[ContentChunk]:
        """Chunk a specific section of content"""
        if len(content.strip()) == 0:
            return []

        # Use the appropriate splitter based on content type
        if source_file.endswith('.md'):
            split_docs = self.markdown_splitter.split_text(content)
        else:
            split_docs = self.text_splitter.split_text(content)

        chunks = []
        for i, doc in enumerate(split_docs):
            chunk_id = f"{source_file}_{section_id}_{i}"

            chunk = ContentChunk(
                id=chunk_id,
                content=doc,
                metadata={
                    'section_id': section_id,
                    'chunk_index_in_section': i,
                    'source_file': source_file,
                    'original_length': len(content),
                    'chunk_length': len(doc),
                    'chunk_ratio': len(doc) / len(content) if len(content) > 0 else 0
                },
                source_file=source_file,
                chunk_index=i
            )
            chunks.append(chunk)

        return chunks

    def chunk_by_content_type(self, content: str, source_file: str, content_type: str = "auto") -> List[ContentChunk]:
        """Chunk content based on its type (markdown, code, plain text, etc.)"""
        if content_type == "auto":
            if source_file.endswith('.md'):
                content_type = "markdown"
            elif any(source_file.endswith(ext) for ext in ['.py', '.js', '.ts', '.cpp', '.java', '.json', '.yaml', '.xml']):
                content_type = "code"
            else:
                content_type = "text"

        if content_type == "markdown":
            return self._chunk_markdown(content, source_file)
        elif content_type == "code":
            return self._chunk_code(content, source_file)
        else:
            return self._chunk_text(content, source_file)

    def _chunk_markdown(self, content: str, source_file: str) -> List[ContentChunk]:
        """Specialized chunking for markdown content"""
        # Preserve code blocks as single units
        parts = []
        current_pos = 0

        # Find all code blocks
        code_block_pattern = r'```.*?\n.*?\n```'
        code_matches = list(re.finditer(code_block_pattern, content, re.DOTALL))

        for match in code_matches:
            # Add content before code block
            if match.start() > current_pos:
                before_content = content[current_pos:match.start()]
                if before_content.strip():
                    parts.append(('text', before_content))

            # Add code block as single unit
            code_content = match.group(0)
            parts.append(('code', code_content))

            current_pos = match.end()

        # Add remaining content after last code block
        if current_pos < len(content):
            remaining = content[current_pos:]
            if remaining.strip():
                parts.append(('text', remaining))

        # Process each part appropriately
        chunks = []
        for part_type, part_content in parts:
            if part_type == 'code':
                # Keep code blocks as single chunks if they're not too large
                if len(part_content) <= self.config.chunk_size * 2:
                    chunk_id = f"{source_file}_code_{len(chunks)}"
                    chunk = ContentChunk(
                        id=chunk_id,
                        content=part_content,
                        metadata={
                            'part_type': 'code',
                            'source_file': source_file,
                            'original_length': len(part_content)
                        },
                        source_file=source_file,
                        chunk_index=len(chunks)
                    )
                    chunks.append(chunk)
                else:
                    # If code block is too large, split it normally
                    normal_chunks = self._chunk_section(part_content, source_file, f"code_split_{len(chunks)}")
                    chunks.extend(normal_chunks)
            else:
                # Process text content normally
                text_chunks = self._chunk_section(part_content, source_file, f"text_{len(chunks)}")
                chunks.extend(text_chunks)

        return chunks

    def _chunk_code(self, content: str, source_file: str) -> List[ContentChunk]:
        """Specialized chunking for code content"""
        # Try to preserve logical code units like functions, classes, etc.
        chunks = []

        # Look for function definitions
        func_pattern = r'(def\s+\w+\s*\(.*?\):(?:\s*\n\s+.*?)*?(?=\n\w|\n\s*def|\n\s*class|\Z))'
        class_pattern = r'(class\s+\w+.*?:(?:\s*\n\s+.*?)*?(?=\n\w|\n\s*def|\n\s*class|\Z))'

        # For now, use regular splitting for code
        return self._chunk_section(content, source_file, "code")

    def _chunk_text(self, content: str, source_file: str) -> List[ContentChunk]:
        """Regular text chunking"""
        return self._chunk_section(content, source_file, "text")

    def chunk_with_overlap_strategy(self, content: str, source_file: str, strategy: str = "overlap") -> List[ContentChunk]:
        """Chunk content using different overlap strategies"""
        if strategy == "overlap":
            return self._chunk_section(content, source_file, "overlap")
        elif strategy == "boundary":
            return self.chunk_by_semantic_boundaries(content, source_file)
        elif strategy == "content_type":
            return self.chunk_by_content_type(content, source_file)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")

    def validate_chunks(self, chunks: List[ContentChunk]) -> Dict[str, Any]:
        """Validate chunk quality and provide metrics"""
        if not chunks:
            return {
                'total_chunks': 0,
                'avg_chunk_size': 0,
                'total_content_length': 0,
                'valid': True,
                'issues': []
            }

        total_content_length = sum(len(chunk.content) for chunk in chunks)
        avg_chunk_size = total_content_length / len(chunks)

        issues = []
        for i, chunk in enumerate(chunks):
            if len(chunk.content.strip()) == 0:
                issues.append(f"Chunk {i} has empty content")
            if len(chunk.content) > self.config.chunk_size * 1.5:
                issues.append(f"Chunk {i} is too large: {len(chunk.content)} chars")

        return {
            'total_chunks': len(chunks),
            'avg_chunk_size': avg_chunk_size,
            'total_content_length': total_content_length,
            'valid': len(issues) == 0,
            'issues': issues
        }

    def merge_small_chunks(self, chunks: List[ContentChunk], min_size: int = 200) -> List[ContentChunk]:
        """Merge small chunks with adjacent chunks to meet minimum size requirements"""
        if len(chunks) <= 1:
            return chunks

        merged_chunks = []
        i = 0

        while i < len(chunks):
            current_chunk = chunks[i]

            # If current chunk is large enough, add it as is
            if len(current_chunk.content) >= min_size:
                merged_chunks.append(current_chunk)
                i += 1
            else:
                # Try to merge with next chunk
                if i + 1 < len(chunks):
                    next_chunk = chunks[i + 1]
                    merged_content = current_chunk.content + "\n\n" + next_chunk.content
                    merged_metadata = {**current_chunk.metadata, **next_chunk.metadata}

                    # Create merged chunk
                    merged_chunk = ContentChunk(
                        id=f"{current_chunk.id}_merged_{next_chunk.id}",
                        content=merged_content,
                        metadata=merged_metadata,
                        source_file=current_chunk.source_file,
                        chunk_index=current_chunk.chunk_index
                    )

                    # If merged chunk is still too small, try to merge with next-next chunk
                    if len(merged_content) < min_size and i + 2 < len(chunks):
                        next_next_chunk = chunks[i + 2]
                        final_merged_content = merged_content + "\n\n" + next_next_chunk.content
                        final_merged_chunk = ContentChunk(
                            id=f"{merged_chunk.id}_merged_{next_next_chunk.id}",
                            content=final_merged_content,
                            metadata={**merged_chunk.metadata, **next_next_chunk.metadata},
                            source_file=merged_chunk.source_file,
                            chunk_index=merged_chunk.chunk_index
                        )
                        merged_chunks.append(final_merged_chunk)
                        i += 3
                    else:
                        merged_chunks.append(merged_chunk)
                        i += 2
                else:
                    # Last chunk is small but no more chunks to merge with
                    merged_chunks.append(current_chunk)
                    i += 1

        return merged_chunks

# Example usage
if __name__ == "__main__":
    # Initialize service
    chunker = ChunkingService()

    # Sample content
    sample_content = """
# Introduction to Physical AI

Physical AI represents a paradigm shift in artificial intelligence, focusing on the integration of perception, reasoning, and action in physical environments. Unlike traditional AI that operates primarily in digital spaces, Physical AI systems must understand and interact with the physical world through sensors and actuators.

## Core Principles

The embodiment principle states that the body plays a crucial role in shaping the mind and intelligent behavior. In Physical AI, this means that the physical form and sensory-motor capabilities of a system directly influence its cognitive processes.

### Morphological Computation

This principle recognizes that the physical structure of a system can perform computations that would otherwise require complex algorithms. For example, the passive dynamics of a walking robot's legs can contribute to energy-efficient locomotion.
"""

    # Test different chunking strategies
    print("Testing semantic boundary chunking...")
    semantic_chunks = chunker.chunk_by_semantic_boundaries(sample_content, "test.md")
    print(f"Created {len(semantic_chunks)} chunks with semantic boundaries")

    for i, chunk in enumerate(semantic_chunks):
        print(f"Chunk {i}: {len(chunk.content)} chars - {chunk.content[:50]}...")

    print("\nTesting validation...")
    validation = chunker.validate_chunks(semantic_chunks)
    print(f"Validation: {validation}")

    print("\nTesting small chunk merging...")
    merged_chunks = chunker.merge_small_chunks(semantic_chunks)
    print(f"Merged to {len(merged_chunks)} chunks")