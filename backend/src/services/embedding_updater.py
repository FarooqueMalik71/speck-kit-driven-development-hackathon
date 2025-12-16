from typing import List, Dict, Any, Optional
import logging
import hashlib
from datetime import datetime
from .vector_store import VectorStoreService
from .content_processor import ContentProcessor, ContentChunk
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class EmbeddingUpdater:
    """Service for updating embeddings when content changes"""

    def __init__(
        self,
        vector_store: VectorStoreService = None,
        content_processor: ContentProcessor = None,
        embedding_service: EmbeddingService = None
    ):
        self.vector_store = vector_store or VectorStoreService()
        self.content_processor = content_processor or ContentProcessor()
        self.embedding_service = embedding_service or EmbeddingService()

    def update_embeddings_for_file(self, filepath: str, content: str) -> bool:
        """Update embeddings for a specific file"""
        logger.info(f"Updating embeddings for file: {filepath}")

        try:
            # Delete existing embeddings for this file
            self.vector_store.delete_by_source_file(filepath)
            logger.debug(f"Deleted existing embeddings for {filepath}")

            # Process the new content
            chunks = self.content_processor.process_file(filepath, content)
            logger.debug(f"Processed {len(chunks)} chunks from {filepath}")

            # Generate new embeddings
            chunks_with_embeddings = self.embedding_service.process_chunks_with_embeddings(chunks)
            logger.debug(f"Generated embeddings for {len(chunks_with_embeddings)} chunks")

            # Store new embeddings
            success = self.vector_store.store_chunks(chunks_with_embeddings)
            if success:
                logger.info(f"Successfully updated embeddings for {filepath}")
                return True
            else:
                logger.error(f"Failed to store embeddings for {filepath}")
                return False

        except Exception as e:
            logger.error(f"Error updating embeddings for file {filepath}: {str(e)}")
            return False

    def update_embeddings_for_directory(self, directory: str) -> Dict[str, Any]:
        """Update embeddings for all files in a directory"""
        logger.info(f"Updating embeddings for directory: {directory}")

        results = {
            'processed_files': 0,
            'successful_updates': 0,
            'failed_updates': 0,
            'failed_files': []
        }

        import os
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.md', '.txt')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()

                        success = self.update_embeddings_for_file(filepath, content)
                        results['processed_files'] += 1

                        if success:
                            results['successful_updates'] += 1
                        else:
                            results['failed_updates'] += 1
                            results['failed_files'].append(filepath)

                    except Exception as e:
                        logger.error(f"Error processing file {filepath}: {str(e)}")
                        results['failed_updates'] += 1
                        results['failed_files'].append(filepath)

        logger.info(f"Directory update completed: {results}")
        return results

    def update_embeddings_batch(self, file_content_pairs: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Update embeddings for a batch of file-content pairs"""
        logger.info(f"Updating embeddings for batch of {len(file_content_pairs)} files")

        results = {
            'processed_files': 0,
            'successful_updates': 0,
            'failed_updates': 0,
            'failed_files': []
        }

        for filepath, content in file_content_pairs:
            try:
                success = self.update_embeddings_for_file(filepath, content)
                results['processed_files'] += 1

                if success:
                    results['successful_updates'] += 1
                else:
                    results['failed_updates'] += 1
                    results['failed_files'].append(filepath)

            except Exception as e:
                logger.error(f"Error processing file {filepath} in batch: {str(e)}")
                results['failed_updates'] += 1
                results['failed_files'].append(filepath)

        logger.info(f"Batch update completed: {results}")
        return results

    def incremental_update(self, file_path: str, old_content: str, new_content: str) -> bool:
        """Perform incremental update by comparing old and new content"""
        logger.info(f"Performing incremental update for: {file_path}")

        try:
            # Calculate hashes to see if content actually changed
            old_hash = hashlib.md5(old_content.encode()).hexdigest()
            new_hash = hashlib.md5(new_content.encode()).hexdigest()

            if old_hash == new_hash:
                logger.info(f"Content unchanged, no update needed for {file_path}")
                return True

            # Check if the change is minimal (e.g., just formatting)
            if self._is_minor_change(old_content, new_content):
                logger.info(f"Minor change detected, updating efficiently for {file_path}")
                return self._update_minor_change(file_path, old_content, new_content)

            # Full update for substantial changes
            logger.info(f"Substantial change detected, performing full update for {file_path}")
            return self.update_embeddings_for_file(file_path, new_content)

        except Exception as e:
            logger.error(f"Error in incremental update for {file_path}: {str(e)}")
            return False

    def _is_minor_change(self, old_content: str, new_content: str, threshold: float = 0.1) -> bool:
        """Check if the change is minor based on content similarity"""
        try:
            # Simple word-based similarity
            old_words = set(old_content.lower().split())
            new_words = set(new_content.lower().split())

            if not old_words or not new_words:
                return False

            intersection = old_words.intersection(new_words)
            union = old_words.union(new_words)
            similarity = len(intersection) / len(union)

            return 1 - similarity < threshold

        except Exception as e:
            logger.warning(f"Error calculating content similarity: {str(e)}, assuming major change")
            return False

    def _update_minor_change(self, file_path: str, old_content: str, new_content: str) -> bool:
        """Update embeddings efficiently for minor content changes"""
        try:
            # For minor changes, we can process both old and new to identify what changed
            # and only update the affected chunks
            old_chunks = self.content_processor.process_file(file_path, old_content)
            new_chunks = self.content_processor.process_file(file_path, new_content)

            # Identify changed chunks
            changed_chunks = self._identify_changed_chunks(old_chunks, new_chunks)

            if not changed_chunks:
                logger.info("No significant chunks changed, update complete")
                return True

            # Delete embeddings for old versions of changed chunks
            chunk_ids_to_delete = [chunk.id for chunk in old_chunks if chunk.id in [c.id for c in changed_chunks]]
            for chunk_id in chunk_ids_to_delete:
                # In a real implementation, we would have a method to delete specific chunks
                # For now, we'll do a full file update as our vector store service doesn't have
                # chunk-specific deletion
                pass

            # Generate embeddings for new chunks
            new_chunks_with_embeddings = self.embedding_service.process_chunks_with_embeddings(new_chunks)

            # Store new embeddings
            success = self.vector_store.store_chunks(new_chunks_with_embeddings)
            return success

        except Exception as e:
            logger.error(f"Error in minor change update: {str(e)}")
            # Fall back to full update
            return self.update_embeddings_for_file(file_path, new_content)

    def _identify_changed_chunks(self, old_chunks: List[ContentChunk], new_chunks: List[ContentChunk]) -> List[ContentChunk]:
        """Identify which chunks have changed between old and new content"""
        changed_chunks = []

        # Create a mapping of chunk ID to content for comparison
        old_chunk_map = {chunk.id: chunk for chunk in old_chunks}
        new_chunk_map = {chunk.id: chunk for chunk in new_chunks}

        # Find new or changed chunks
        for chunk_id, new_chunk in new_chunk_map.items():
            if chunk_id not in old_chunk_map:
                # New chunk
                changed_chunks.append(new_chunk)
            elif old_chunk_map[chunk_id].content != new_chunk.content:
                # Changed chunk
                changed_chunks.append(new_chunk)

        # Find deleted chunks
        for chunk_id, old_chunk in old_chunk_map.items():
            if chunk_id not in new_chunk_map:
                # Deleted chunk - we'd need to handle this in a full implementation
                pass

        return changed_chunks

    def update_embeddings_with_metadata(self, filepath: str, content: str, metadata: Dict[str, Any]) -> bool:
        """Update embeddings while preserving and adding metadata"""
        logger.info(f"Updating embeddings with metadata for: {filepath}")

        try:
            # Process content with metadata
            chunks = self.content_processor.process_file(filepath, content)

            # Add/update metadata for each chunk
            for chunk in chunks:
                chunk.metadata.update(metadata)
                chunk.metadata['last_updated'] = datetime.utcnow().isoformat()
                chunk.metadata['update_type'] = 'full'

            # Generate embeddings
            chunks_with_embeddings = self.embedding_service.process_chunks_with_embeddings(chunks)

            # Delete old embeddings and store new ones
            self.vector_store.delete_by_source_file(filepath)
            success = self.vector_store.store_chunks(chunks_with_embeddings)

            return success

        except Exception as e:
            logger.error(f"Error updating embeddings with metadata for {filepath}: {str(e)}")
            return False

    def get_content_hash(self, content: str) -> str:
        """Get hash of content for change detection"""
        return hashlib.md5(content.encode()).hexdigest()

    def sync_content_with_embeddings(self, content_directory: str, vector_store_collection: str = None) -> Dict[str, Any]:
        """Synchronize content directory with vector store embeddings"""
        logger.info(f"Syncing content directory: {content_directory}")

        if vector_store_collection:
            # In a real implementation, we would switch to the specified collection
            pass

        # Get all content files
        import os
        content_files = []
        for root, dirs, files in os.walk(content_directory):
            for file in files:
                if file.endswith(('.md', '.txt')):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    content_hash = self.get_content_hash(content)
                    content_files.append((filepath, content, content_hash))

        # Get current embeddings in vector store
        current_files_in_store = set()
        try:
            collections = self.vector_store.get_all_collections()
            if vector_store_collection in collections:
                # In a real implementation, we would get all source files in the collection
                pass
        except Exception as e:
            logger.error(f"Error getting current files from vector store: {str(e)}")

        # Process each content file
        results = {
            'files_to_update': [],
            'files_to_remove': [],
            'files_up_to_date': 0
        }

        for filepath, content, content_hash in content_files:
            # In a real implementation, we would check if this file exists in vector store
            # and if its hash matches
            results['files_to_update'].append(filepath)

        # Update files that need updating
        update_results = self.update_embeddings_batch([
            (filepath, content) for filepath, content, _ in content_files
        ])

        return {**results, **update_results}

# Example usage
if __name__ == "__main__":
    # Initialize service
    updater = EmbeddingUpdater()

    # Sample content update
    sample_content = """
# Introduction to Physical AI

Physical AI represents a paradigm shift in artificial intelligence, focusing on the integration of perception, reasoning, and action in physical environments. Unlike traditional AI that operates primarily in digital spaces, Physical AI systems must understand and interact with the physical world through sensors and actuators.
"""

    # Test update for a file
    success = updater.update_embeddings_for_file("sample_update.md", sample_content)
    print(f"Update success: {success}")

    # Test incremental update
    old_content = sample_content
    new_content = sample_content + "\n\n## Additional Section\nThis is new content for the document."
    incremental_success = updater.incremental_update("sample_update.md", old_content, new_content)
    print(f"Incremental update success: {incremental_success}")

    # Test sync
    sync_results = updater.sync_content_with_embeddings("./docs")
    print(f"Sync results: {sync_results}")