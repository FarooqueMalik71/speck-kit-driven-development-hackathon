import unittest
from unittest.mock import Mock, patch
from src.services.content_processor import ContentProcessor
from src.models.content_chunk import ContentChunk
from datetime import datetime


class TestContentProcessor(unittest.TestCase):
    """
    Unit tests for ContentProcessor
    """

    def setUp(self):
        """
        Set up test fixtures
        """
        self.processor = ContentProcessor(chunk_size=500, chunk_overlap=50)

    def test_init(self):
        """
        Test that ContentProcessor initializes correctly
        """
        self.assertEqual(self.processor.chunk_size, 500)
        self.assertEqual(self.processor.chunk_overlap, 50)
        self.assertIsNotNone(self.processor.text_splitter)

    def test_extract_metadata_from_source(self):
        """
        Test that metadata is correctly extracted from source
        """
        source_url = "https://example.com/page"
        content = "This is some test content with multiple words."

        metadata = self.processor.extract_metadata_from_source(source_url, content)

        self.assertEqual(metadata['source_url'], source_url)
        self.assertIn('created_at', metadata)
        self.assertEqual(metadata['word_count'], 8)
        self.assertEqual(metadata['char_count'], len(content))

    def test_clean_content(self):
        """
        Test that content cleaning works properly
        """
        dirty_content = "This is content with\n\n\nmultiple\n\nnewlines and   extra   spaces.\n\n```\ncode block\n```\nAnd {#anchor-links}."

        cleaned = self.processor.clean_content(dirty_content)

        # Should preserve single newlines, collapse multiple ones
        self.assertNotIn("\n\n\n", cleaned)
        # Should remove extra spaces
        self.assertNotIn("   ", cleaned)
        # Should remove code blocks
        self.assertNotIn("```\ncode block\n```", cleaned)
        # Should remove anchor links
        self.assertNotIn("{#anchor-links}", cleaned)

    def test_extract_content_from_markdown(self):
        """
        Test that markdown elements are properly extracted
        """
        markdown_content = "# Title\n\nThis is **bold** and *italic* content.\n\n[Link text](http://example.com)\n\n![Alt text](image.jpg)\n\n`inline code`"

        extracted = self.processor.extract_content_from_markdown(markdown_content)

        # Should remove markdown elements but preserve the text content
        self.assertIn("Title", extracted)
        self.assertIn("bold", extracted)
        self.assertIn("italic", extracted)
        self.assertIn("Link text", extracted)  # Link text should remain
        self.assertIn("Alt text", extracted)  # Image alt text should remain
        self.assertIn("inline code", extracted)  # Inline code text should remain

        # Should remove markdown syntax
        self.assertNotIn("**", extracted)
        self.assertNotIn("*", extracted)
        self.assertNotIn("[](", extracted)  # Link brackets and parentheses
        self.assertNotIn("![](", extracted)  # Image syntax
        self.assertNotIn("`", extracted)  # Code syntax

    def test_process_file(self):
        """
        Test that a file is processed into chunks correctly
        """
        source_url = "https://example.com/test-page"
        content = """
        # Introduction

        This is the introduction section with some content to be processed.

        ## Subsection

        This is a subsection with more content that will be split into multiple chunks if needed.

        The content continues here with additional paragraphs and sections.
        """

        chunks = self.processor.process_file(source_url, content)

        # Should create at least one chunk
        self.assertGreaterEqual(len(chunks), 1)

        # Each chunk should be a ContentChunk instance
        for chunk in chunks:
            self.assertIsInstance(chunk, ContentChunk)
            self.assertTrue(chunk.id.startswith(self.processor.extract_metadata_from_source(source_url, content)['file_hash']))
            self.assertEqual(chunk.source_url, source_url)
            self.assertLessEqual(len(chunk.content), self.processor.chunk_size)
            self.assertIsNotNone(chunk.created_at)

    def test_validate_chunk_quality_pass(self):
        """
        Test that valid chunks pass quality validation
        """
        chunk = ContentChunk(
            id="test_id",
            content="This is valid content with meaningful text.",
            source_url="https://example.com/test",
            section_title="Test Section",
            chunk_index=0,
            created_at=datetime.now()
        )

        result = self.processor.validate_chunk_quality(chunk)

        self.assertTrue(result)

    def test_validate_chunk_quality_fail_small(self):
        """
        Test that small chunks fail quality validation
        """
        chunk = ContentChunk(
            id="test_id",
            content="Hi",  # Very short content
            source_url="https://example.com/test",
            section_title="Test Section",
            chunk_index=0,
            created_at=datetime.now()
        )

        result = self.processor.validate_chunk_quality(chunk)

        self.assertFalse(result)

    def test_validate_chunk_quality_fail_whitespace(self):
        """
        Test that chunks with only whitespace fail quality validation
        """
        chunk = ContentChunk(
            id="test_id",
            content="    \n\t   \n\n    ",  # Mostly whitespace
            source_url="https://example.com/test",
            section_title="Test Section",
            chunk_index=0,
            created_at=datetime.now()
        )

        result = self.processor.validate_chunk_quality(chunk)

        self.assertFalse(result)

    def test_get_content_statistics_empty(self):
        """
        Test content statistics for empty list
        """
        stats = self.processor.get_content_statistics([])

        self.assertEqual(stats['total_chunks'], 0)
        self.assertEqual(stats['total_chars'], 0)
        self.assertEqual(stats['avg_chunk_size'], 0)
        self.assertEqual(stats['min_chunk_size'], 0)
        self.assertEqual(stats['max_chunk_size'], 0)

    def test_get_content_statistics(self):
        """
        Test content statistics for a list of chunks
        """
        chunks = [
            ContentChunk(
                id="id1",
                content="First chunk with some content",
                source_url="https://example.com/test",
                section_title="Section 1",
                chunk_index=0,
                created_at=datetime.now()
            ),
            ContentChunk(
                id="id2",
                content="Second chunk with more content to test statistics",
                source_url="https://example.com/test",
                section_title="Section 2",
                chunk_index=1,
                created_at=datetime.now()
            )
        ]

        stats = self.processor.get_content_statistics(chunks)

        self.assertEqual(stats['total_chunks'], 2)
        self.assertGreater(stats['total_chars'], 0)
        self.assertGreater(stats['avg_chunk_size'], 0)
        self.assertGreaterEqual(stats['min_chunk_size'], 0)
        self.assertGreaterEqual(stats['max_chunk_size'], 0)
        self.assertEqual(stats['valid_chunks'], 2)


if __name__ == '__main__':
    unittest.main()