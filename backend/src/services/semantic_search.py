from typing import List, Dict, Any, Optional, Tuple
import logging
from .vector_store import VectorStoreService
from .embedding_service import EmbeddingService
from .content_processor import ContentChunk

logger = logging.getLogger(__name__)

class SemanticSearchService:
    """Service for performing semantic search against vector store"""

    def __init__(self, vector_store: VectorStoreService = None, embedding_service: EmbeddingService = None):
        self.vector_store = vector_store or VectorStoreService()
        self.embedding_service = embedding_service or EmbeddingService()

    def search(self, query: str, limit: int = 10, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Perform semantic search using the query against vector store"""
        logger.info(f"Performing semantic search for query: '{query[:50]}...'")

        try:
            # Generate embedding for the query
            query_embedding = self.embedding_service.generate_embedding(query)

            # Search in vector store
            results = self.vector_store.search(query_embedding, limit=limit, filters=filters)

            logger.info(f"Semantic search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []

    def search_with_hybrid_ranking(self, query: str, limit: int = 10, keyword_weight: float = 0.3) -> List[Dict[str, Any]]:
        """Perform hybrid search combining semantic and keyword matching"""
        logger.info(f"Performing hybrid search for query: '{query[:50]}...'")

        try:
            # Get semantic results
            semantic_results = self.search(query, limit=limit*2)  # Get more results for hybrid ranking

            # Normalize scores
            if semantic_results:
                max_semantic_score = max(result['score'] for result in semantic_results)
                for result in semantic_results:
                    result['semantic_score'] = result['score'] / max_semantic_score if max_semantic_score > 0 else 0
                    result['hybrid_score'] = result['semantic_score'] * (1 - keyword_weight)

            # TODO: Implement keyword search and combine scores
            # For now, return semantic results with hybrid score calculated
            # In a full implementation, we would also perform keyword search and combine scores

            # Sort by hybrid score
            sorted_results = sorted(semantic_results, key=lambda x: x['hybrid_score'], reverse=True)

            logger.info(f"Hybrid search returned {len(sorted_results)} results")
            return sorted_results[:limit]

        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            return []

    def search_in_selected_content(self, query: str, selected_content_ids: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search limited to selected content chunks"""
        logger.info(f"Performing selected content search for query: '{query[:50]}...' in {len(selected_content_ids)} chunks")

        try:
            # Generate embedding for the query
            query_embedding = self.embedding_service.generate_embedding(query)

            # Create filter for selected content IDs
            filters = {"id": {"$in": selected_content_ids}}

            # Search in vector store with filters
            results = self.vector_store.search(query_embedding, limit=limit, filters=filters)

            logger.info(f"Selected content search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error in selected content search: {str(e)}")
            return []

    def find_related_content(self, content_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find content related to a specific chunk by using its embedding"""
        logger.info(f"Finding related content for chunk: {content_id}")

        try:
            # Get the content chunk to use its embedding as query
            chunk_data = self.vector_store.get_content_by_id(content_id)
            if not chunk_data:
                logger.warning(f"Content chunk not found: {content_id}")
                return []

            # Generate embedding for the content
            content_embedding = self.embedding_service.generate_embedding(chunk_data['content'])

            # Search for similar content, excluding the original chunk
            results = self.vector_store.search(content_embedding, limit=limit+1)  # +1 to exclude original

            # Filter out the original chunk
            related_results = [result for result in results if result['id'] != content_id]

            logger.info(f"Found {len(related_results)} related chunks")
            return related_results[:limit]

        except Exception as e:
            logger.error(f"Error finding related content: {str(e)}")
            return []

    def get_content_relevance_scores(self, query: str, content_list: List[str]) -> List[Tuple[str, float]]:
        """Get relevance scores for a list of content strings against a query"""
        logger.info(f"Getting relevance scores for {len(content_list)} content items")

        try:
            # Generate embedding for the query
            query_embedding = self.embedding_service.generate_embedding(query)

            scores = []
            for content in content_list:
                # Generate embedding for each content
                content_embedding = self.embedding_service.generate_embedding(content)

                # Calculate cosine similarity
                import numpy as np
                query_array = np.array(query_embedding)
                content_array = np.array(content_embedding)

                # Calculate cosine similarity
                cosine_sim = np.dot(query_array, content_array) / (
                    np.linalg.norm(query_array) * np.linalg.norm(content_array)
                )

                scores.append((content, float(cosine_sim)))

            # Sort by relevance score
            sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

            logger.info("Successfully calculated relevance scores")
            return sorted_scores

        except Exception as e:
            logger.error(f"Error calculating relevance scores: {str(e)}")
            return []

    def search_with_context_awareness(self, query: str, context: Optional[Dict] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform search with additional context awareness"""
        logger.info(f"Performing context-aware search for query: '{query[:50]}...'")

        try:
            # Modify query based on context if provided
            enhanced_query = query
            if context:
                if 'user_level' in context:
                    level_modifier = {
                        'beginner': 'Explain in simple terms',
                        'intermediate': 'Provide detailed explanation',
                        'advanced': 'Give technical details'
                    }
                    if context['user_level'] in level_modifier:
                        enhanced_query = f"{query}. {level_modifier[context['user_level']]}."

                if 'topic_focus' in context:
                    enhanced_query = f"{context['topic_focus']}: {enhanced_query}"

            # Perform search with enhanced query
            results = self.search(enhanced_query, limit=limit)

            # Optionally filter results based on context
            if context and 'exclude_topics' in context:
                excluded_topics = context['exclude_topics']
                results = [
                    result for result in results
                    if not any(excluded_topic.lower() in result['content'].lower() for excluded_topic in excluded_topics)
                ]

            logger.info(f"Context-aware search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error in context-aware search: {str(e)}")
            return []

    def search_with_diversity(self, query: str, limit: int = 10, diversity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Perform search ensuring diverse results to avoid repetitive content"""
        logger.info(f"Performing diversity-aware search for query: '{query[:50]}...'")

        try:
            # Get more results than needed for diversity selection
            raw_results = self.search(query, limit=limit * 3)

            if not raw_results:
                return []

            # Select diverse results
            diverse_results = [raw_results[0]]  # Always include the top result

            for result in raw_results[1:]:
                is_diverse = True
                for selected_result in diverse_results:
                    # Calculate similarity between result and already selected results
                    similarity = self._calculate_content_similarity(
                        result['content'],
                        selected_result['content']
                    )
                    if similarity > diversity_threshold:
                        is_diverse = False
                        break

                if is_diverse:
                    diverse_results.append(result)
                    if len(diverse_results) >= limit:
                        break

            logger.info(f"Diversity-aware search returned {len(diverse_results)} results")
            return diverse_results

        except Exception as e:
            logger.error(f"Error in diversity-aware search: {str(e)}")
            # Fall back to regular search
            return self.search(query, limit=limit)

    def _calculate_content_similarity(self, content1: str, content2: str, threshold: float = 50) -> float:
        """Calculate similarity between two content strings"""
        try:
            # Use embeddings to calculate similarity
            emb1 = self.embedding_service.generate_embedding(content1[:threshold])  # Limit for efficiency
            emb2 = self.embedding_service.generate_embedding(content2[:threshold])

            import numpy as np
            array1 = np.array(emb1)
            array2 = np.array(emb2)

            # Calculate cosine similarity
            similarity = np.dot(array1, array2) / (np.linalg.norm(array1) * np.linalg.norm(array2))
            return float(similarity)

        except Exception as e:
            logger.warning(f"Error calculating content similarity: {str(e)}, using fallback")
            # Fallback: simple overlap calculation
            words1 = set(content1.lower().split()[:threshold])
            words2 = set(content2.lower().split()[:threshold])
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            return len(intersection) / len(union) if union else 0

    def multi_query_search(self, queries: List[str], limit_per_query: int = 5) -> List[Dict[str, Any]]:
        """Perform multiple related queries and combine results"""
        logger.info(f"Performing multi-query search with {len(queries)} queries")

        try:
            all_results = []
            for i, query in enumerate(queries):
                logger.debug(f"Processing query {i+1}/{len(queries)}: '{query[:30]}...'")

                query_results = self.search(query, limit=limit_per_query)
                # Add query identifier to results
                for result in query_results:
                    result['source_query'] = query
                    result['query_rank'] = i

                all_results.extend(query_results)

            # Remove duplicates based on content ID
            seen_ids = set()
            unique_results = []
            for result in all_results:
                if result['id'] not in seen_ids:
                    seen_ids.add(result['id'])
                    unique_results.append(result)

            # Re-rank based on combined relevance
            final_results = sorted(unique_results, key=lambda x: x['score'], reverse=True)

            logger.info(f"Multi-query search returned {len(final_results)} unique results")
            return final_results

        except Exception as e:
            logger.error(f"Error in multi-query search: {str(e)}")
            return []

# Example usage
if __name__ == "__main__":
    # Initialize services
    search_service = SemanticSearchService()

    # Sample query
    query = "What is Physical AI?"
    results = search_service.search(query, limit=5)

    print(f"Search results for '{query}':")
    for i, result in enumerate(results):
        print(f"{i+1}. Score: {result['score']:.3f}")
        print(f"   Content: {result['content'][:100]}...")
        print(f"   Source: {result['source_file']}")
        print()

    # Test context-aware search
    context = {
        'user_level': 'beginner',
        'topic_focus': 'embodied intelligence'
    }
    context_results = search_service.search_with_context_awareness(
        "embodiment in AI", context, limit=3
    )
    print(f"Context-aware search results:")
    for i, result in enumerate(context_results):
        print(f"{i+1}. Score: {result['score']:.3f}")
        print(f"   Content: {result['content'][:100]}...")
        print()