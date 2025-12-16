from typing import List, Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from .vector_store import VectorStoreService
from .semantic_search import SemanticSearchService
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    """Structured result from content retrieval"""
    id: str
    content: str
    source_file: str
    score: float
    metadata: Dict[str, Any]
    relevance_score: float
    context_similarity: float
    is_relevant: bool

class RetrievalService:
    """Service for retrieving and ranking content with relevance scoring"""

    def __init__(
        self,
        vector_store: VectorStoreService = None,
        semantic_search: SemanticSearchService = None,
        embedding_service: EmbeddingService = None
    ):
        self.vector_store = vector_store or VectorStoreService()
        self.semantic_search = semantic_search or SemanticSearchService(
            vector_store=self.vector_store,
            embedding_service=embedding_service
        )
        self.embedding_service = embedding_service or EmbeddingService()

    def retrieve_content(
        self,
        query: str,
        limit: int = 10,
        min_relevance_score: float = 0.3,
        filters: Optional[Dict] = None
    ) -> List[RetrievalResult]:
        """Retrieve content with relevance scoring and filtering"""
        logger.info(f"Retrieving content for query: '{query[:50]}...'")

        try:
            # Perform semantic search
            search_results = self.semantic_search.search(query, limit=limit*2, filters=filters)

            # Calculate additional relevance metrics
            retrieval_results = []
            query_embedding = self.embedding_service.generate_embedding(query)

            for result in search_results:
                # Calculate relevance score (combines multiple factors)
                relevance_score = self._calculate_relevance_score(
                    query,
                    result['content'],
                    result['score']  # base semantic score
                )

                # Calculate context similarity
                context_similarity = self._calculate_context_similarity(query, result['content'])

                # Determine if result is relevant based on threshold
                is_relevant = relevance_score >= min_relevance_score

                retrieval_result = RetrievalResult(
                    id=result['id'],
                    content=result['content'],
                    source_file=result['source_file'],
                    score=result['score'],  # raw semantic score
                    metadata=result['metadata'],
                    relevance_score=relevance_score,
                    context_similarity=context_similarity,
                    is_relevant=is_relevant
                )

                retrieval_results.append(retrieval_result)

            # Sort by relevance score and filter by relevance threshold
            sorted_results = sorted(retrieval_results, key=lambda x: x.relevance_score, reverse=True)
            filtered_results = [r for r in sorted_results if r.is_relevant]

            logger.info(f"Retrieved {len(filtered_results)} relevant results out of {len(retrieval_results)} total")
            return filtered_results[:limit]

        except Exception as e:
            logger.error(f"Error in content retrieval: {str(e)}")
            return []

    def _calculate_relevance_score(self, query: str, content: str, semantic_score: float) -> float:
        """Calculate comprehensive relevance score combining multiple factors"""
        # Start with the base semantic similarity score
        score = semantic_score

        # Factor 1: Content length appropriateness (not too short or too long)
        content_length_score = self._calculate_length_score(content)
        score = (score * 0.7) + (content_length_score * 0.3)

        # Factor 2: Keyword overlap between query and content
        keyword_overlap_score = self._calculate_keyword_overlap_score(query, content)
        score = (score * 0.6) + (keyword_overlap_score * 0.4)

        # Factor 3: Position of matching terms (early content might be more relevant)
        position_score = self._calculate_position_score(query, content)
        score = (score * 0.6) + (position_score * 0.4)

        # Normalize to 0-1 range
        return min(max(score, 0.0), 1.0)

    def _calculate_length_score(self, content: str) -> float:
        """Calculate score based on content length appropriateness"""
        word_count = len(content.split())

        # Optimal range is around 100-500 words
        if 50 <= word_count <= 1000:
            return 1.0
        elif 20 <= word_count < 50 or 1000 < word_count <= 2000:
            return 0.7
        else:
            return 0.3  # Too short or too long

    def _calculate_keyword_overlap_score(self, query: str, content: str) -> float:
        """Calculate score based on keyword overlap between query and content"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        if not query_words:
            return 0.0

        overlap = query_words.intersection(content_words)
        overlap_ratio = len(overlap) / len(query_words)

        # Boost score if important terms from query are found
        important_terms = ['physical ai', 'embodied intelligence', 'robotics', 'humanoid', 'ros', 'simulation']
        important_matches = any(term in content.lower() for term in important_terms)

        if important_matches and overlap_ratio > 0:
            overlap_ratio *= 1.2  # Boost if important terms are found

        return min(overlap_ratio, 1.0)

    def _calculate_position_score(self, query: str, content: str) -> float:
        """Calculate score based on where matching terms appear in content"""
        query_words = query.lower().split()
        content_lower = content.lower()

        # Find the average position of query words in content
        total_position = 0
        matches_found = 0

        for word in query_words:
            pos = content_lower.find(word)
            if pos != -1:
                # Normalize position to 0-1 (earlier is better)
                normalized_pos = 1.0 - (pos / len(content_lower))
                total_position += normalized_pos
                matches_found += 1

        if matches_found == 0:
            return 0.0

        avg_position_score = total_position / matches_found
        return avg_position_score

    def _calculate_context_similarity(self, query: str, content: str) -> float:
        """Calculate how well the content matches the context of the query"""
        try:
            query_embedding = self.embedding_service.generate_embedding(query)
            content_embedding = self.embedding_service.generate_embedding(content)

            import numpy as np
            q_array = np.array(query_embedding)
            c_array = np.array(content_embedding)

            # Calculate cosine similarity
            similarity = np.dot(q_array, c_array) / (np.linalg.norm(q_array) * np.linalg.norm(c_array))
            return float(similarity)

        except Exception as e:
            logger.warning(f"Error calculating context similarity: {str(e)}")
            return 0.0

    def retrieve_with_query_expansion(self, query: str, limit: int = 10) -> List[RetrievalResult]:
        """Retrieve content using query expansion techniques"""
        logger.info(f"Retrieving with query expansion for: '{query[:50]}...'")

        # Expand the query with related terms
        expanded_queries = self._expand_query(query)

        # Perform search with original and expanded queries
        all_results = []
        for expanded_query in expanded_queries:
            results = self.retrieve_content(expanded_query, limit=limit//len(expanded_queries))
            all_results.extend(results)

        # Remove duplicates and rerank
        unique_results = self._remove_duplicate_results(all_results)
        reranked_results = sorted(unique_results, key=lambda x: x.relevance_score, reverse=True)

        logger.info(f"Query expansion retrieval returned {len(reranked_results)} results")
        return reranked_results[:limit]

    def _expand_query(self, query: str) -> List[str]:
        """Expand query with related terms and synonyms"""
        expanded_queries = [query]

        # Add related terms based on domain knowledge
        domain_expansions = {
            'physical ai': ['embodied ai', 'embodied intelligence', 'robotics ai'],
            'embodied intelligence': ['embodied cognition', 'physical ai', 'robotics'],
            'humanoid robotics': ['humanoid robot', 'bipedal robot', 'human-like robot'],
            'ros': ['robot operating system', 'ros2', 'robotics framework'],
            'simulation': ['gazebo', 'robot simulation', 'physics simulation'],
            'control': ['robot control', 'motion control', 'feedback control'],
            'kinematics': ['forward kinematics', 'inverse kinematics', 'robot motion'],
            'perception': ['computer vision', 'sensor fusion', 'object detection'],
            'manipulation': ['robot manipulation', 'grasping', 'pick and place'],
            'navigation': ['path planning', 'motion planning', 'mobile robots']
        }

        query_lower = query.lower()
        for term, expansions in domain_expansions.items():
            if term in query_lower:
                for expansion in expansions:
                    expanded_queries.append(f"{query} {expansion}")

        # Add broader context terms
        if 'physical' in query_lower or 'embodied' in query_lower:
            expanded_queries.extend([
                f"{query} real world interaction",
                f"{query} sensorimotor",
                f"{query} environmental interaction"
            ])

        return list(set(expanded_queries))  # Remove duplicates

    def _remove_duplicate_results(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """Remove duplicate results based on content similarity"""
        if not results:
            return []

        unique_results = [results[0]]  # Always keep the first result

        for result in results[1:]:
            is_duplicate = False
            for unique_result in unique_results:
                # Check if content is similar enough to be considered a duplicate
                similarity = self._calculate_content_similarity(result.content, unique_result.content)
                if similarity > 0.8:  # High similarity threshold for duplicates
                    # Keep the one with higher relevance score
                    if result.relevance_score > unique_result.relevance_score:
                        unique_results.remove(unique_result)
                        unique_results.append(result)
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_results.append(result)

        return unique_results

    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings"""
        try:
            # Use embeddings to calculate similarity
            emb1 = self.embedding_service.generate_embedding(content1[:1000])  # Limit length for efficiency
            emb2 = self.embedding_service.generate_embedding(content2[:1000])

            import numpy as np
            array1 = np.array(emb1)
            array2 = np.array(emb2)

            # Calculate cosine similarity
            similarity = np.dot(array1, array2) / (np.linalg.norm(array1) * np.linalg.norm(array2))
            return float(similarity)

        except Exception as e:
            logger.warning(f"Error calculating content similarity: {str(e)}, using fallback")
            # Fallback: simple overlap calculation
            words1 = set(content1.lower().split()[:100])  # Limit for efficiency
            words2 = set(content2.lower().split()[:100])
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            return len(intersection) / len(union) if union else 0

    def retrieve_for_selected_text_qa(
        self,
        query: str,
        selected_content_ids: List[str],
        limit: int = 5
    ) -> List[RetrievalResult]:
        """Retrieve content specifically for selected-text Q&A mode"""
        logger.info(f"Retrieving for selected-text Q&A: '{query[:50]}...' in {len(selected_content_ids)} chunks")

        try:
            # Search only within selected content
            search_results = self.semantic_search.search_in_selected_content(
                query, selected_content_ids, limit=limit
            )

            # Calculate relevance scores for selected content
            retrieval_results = []
            for result in search_results:
                relevance_score = self._calculate_relevance_score(
                    query,
                    result['content'],
                    result['score']
                )

                retrieval_result = RetrievalResult(
                    id=result['id'],
                    content=result['content'],
                    source_file=result['source_file'],
                    score=result['score'],
                    metadata=result['metadata'],
                    relevance_score=relevance_score,
                    context_similarity=self._calculate_context_similarity(query, result['content']),
                    is_relevant=relevance_score >= 0.1  # Lower threshold for selected text mode
                )

                retrieval_results.append(retrieval_result)

            # Sort by relevance and return
            sorted_results = sorted(retrieval_results, key=lambda x: x.relevance_score, reverse=True)
            logger.info(f"Selected-text retrieval returned {len(sorted_results)} results")
            return sorted_results

        except Exception as e:
            logger.error(f"Error in selected-text retrieval: {str(e)}")
            return []

    def enforce_content_boundaries(
        self,
        query: str,
        selected_content: List[str],
        ai_response: str
    ) -> Dict[str, Any]:
        """Enforce content boundaries by checking if AI response is grounded in selected content"""
        logger.info(f"Enforcing content boundaries for query: '{query[:50]}...'")

        try:
            # Calculate similarity between AI response and selected content
            response_embedding = self.embedding_service.generate_embedding(ai_response)
            content_similarities = []

            for content in selected_content:
                content_embedding = self.embedding_service.generate_embedding(content[:1000])  # Limit for efficiency
                import numpy as np
                response_array = np.array(response_embedding)
                content_array = np.array(content_embedding)

                # Calculate cosine similarity
                similarity = np.dot(response_array, content_array) / (
                    np.linalg.norm(response_array) * np.linalg.norm(content_array)
                )
                content_similarities.append(float(similarity))

            # Calculate average similarity
            avg_similarity = sum(content_similarities) / len(content_similarities) if content_similarities else 0.0

            # Identify specific content that supports the response
            supporting_content = []
            for i, content in enumerate(selected_content):
                if content_similarities[i] > 0.3:  # Threshold for supporting content
                    supporting_content.append({
                        'content': content,
                        'similarity': content_similarities[i],
                        'index': i
                    })

            # Sort supporting content by similarity
            supporting_content.sort(key=lambda x: x['similarity'], reverse=True)

            # Check for hallucinations by looking for content not in selected text
            is_content_valid = avg_similarity > 0.2  # Threshold for content validity

            result = {
                'is_valid_response': is_content_valid,
                'avg_content_similarity': avg_similarity,
                'supporting_content': supporting_content[:3],  # Top 3 supporting pieces
                'boundary_compliance_score': avg_similarity,
                'needs_fact_check': avg_similarity < 0.4,  # Low similarity indicates potential hallucination
                'response_quality': 'high' if avg_similarity > 0.6 else 'medium' if avg_similarity > 0.3 else 'low'
            }

            logger.info(f"Content boundary enforcement result: {result['is_valid_response']} with similarity {result['avg_content_similarity']:.3f}")
            return result

        except Exception as e:
            logger.error(f"Error in content boundary enforcement: {str(e)}")
            return {
                'is_valid_response': False,
                'avg_content_similarity': 0.0,
                'supporting_content': [],
                'boundary_compliance_score': 0.0,
                'needs_fact_check': True,
                'response_quality': 'low'
            }

    def get_retrieval_statistics(self, results: List[RetrievalResult]) -> Dict[str, Any]:
        """Get statistics about retrieval results"""
        if not results:
            return {
                'total_results': 0,
                'avg_relevance_score': 0.0,
                'avg_semantic_score': 0.0,
                'relevant_results': 0,
                'highly_relevant_results': 0,  # relevance_score > 0.7
                'confidence_score': 0.0,
                'retrieval_quality': 'low'
            }

        total_results = len(results)
        avg_relevance = sum(r.relevance_score for r in results) / total_results
        avg_semantic = sum(r.score for r in results) / total_results
        relevant_results = sum(1 for r in results if r.is_relevant)
        highly_relevant_results = sum(1 for r in results if r.relevance_score > 0.7)

        # Calculate overall confidence in retrieval
        confidence_score = self._calculate_retrieval_confidence(results, avg_relevance, avg_semantic)
        retrieval_quality = self._determine_retrieval_quality(confidence_score)

        return {
            'total_results': total_results,
            'avg_relevance_score': avg_relevance,
            'avg_semantic_score': avg_semantic,
            'relevant_results': relevant_results,
            'highly_relevant_results': highly_relevant_results,
            'confidence_score': confidence_score,
            'retrieval_quality': retrieval_quality
        }

    def _calculate_retrieval_confidence(self, results: List[RetrievalResult], avg_relevance: float, avg_semantic: float) -> float:
        """Calculate overall confidence in retrieval results"""
        if not results:
            return 0.0

        # Factor 1: Average relevance score
        relevance_factor = avg_relevance

        # Factor 2: Average semantic similarity
        semantic_factor = avg_semantic

        # Factor 3: Consistency of scores (low variance means high confidence)
        if len(results) > 1:
            relevance_scores = [r.relevance_score for r in results]
            semantic_scores = [r.score for r in results]

            # Calculate variance (lower is better)
            relevance_variance = sum((x - avg_relevance) ** 2 for x in relevance_scores) / len(relevance_scores)
            semantic_variance = sum((x - avg_semantic) ** 2 for x in semantic_scores) / len(semantic_scores)

            # Convert variance to consistency score (inverted)
            relevance_consistency = 1.0 / (1.0 + relevance_variance)
            semantic_consistency = 1.0 / (1.0 + semantic_variance)
        else:
            relevance_consistency = 1.0
            semantic_consistency = 1.0

        # Factor 4: Number of results (more relevant results = higher confidence, up to a point)
        result_count_factor = min(len([r for r in results if r.is_relevant]) / 10.0, 1.0)  # Cap at 1.0 for 10+ results

        # Weighted combination of all factors
        confidence = (
            relevance_factor * 0.3 +
            semantic_factor * 0.2 +
            relevance_consistency * 0.2 +
            semantic_consistency * 0.1 +
            result_count_factor * 0.2
        )

        return min(max(confidence, 0.0), 1.0)

    def _determine_retrieval_quality(self, confidence_score: float) -> str:
        """Determine quality level based on confidence score"""
        if confidence_score >= 0.8:
            return 'high'
        elif confidence_score >= 0.6:
            return 'medium'
        elif confidence_score >= 0.4:
            return 'low'
        else:
            return 'very_low'

    def calculate_response_confidence(
        self,
        query: str,
        retrieved_results: List[RetrievalResult],
        ai_response: str
    ) -> Dict[str, Any]:
        """Calculate confidence in AI response based on retrieval quality and other factors"""
        logger.info(f"Calculating response confidence for query: '{query[:50]}...'")

        try:
            # Get retrieval statistics which includes confidence
            retrieval_stats = self.get_retrieval_statistics(retrieved_results)

            # Calculate content grounding score
            grounding_score = self._calculate_content_grounding_score(ai_response, retrieved_results)

            # Calculate response coherence score
            coherence_score = self._calculate_response_coherence(query, ai_response)

            # Combine scores into overall confidence
            overall_confidence = (
                retrieval_stats['confidence_score'] * 0.5 +
                grounding_score * 0.3 +
                coherence_score * 0.2
            )

            # Determine confidence level
            confidence_level = self._determine_response_confidence_level(overall_confidence)

            result = {
                'overall_confidence': overall_confidence,
                'retrieval_confidence': retrieval_stats['confidence_score'],
                'content_grounding_score': grounding_score,
                'response_coherence_score': coherence_score,
                'confidence_level': confidence_level,
                'retrieval_quality': retrieval_stats['retrieval_quality'],
                'is_confident': overall_confidence > 0.6,  # Threshold for confidence
                'confidence_explanation': self._explain_confidence(
                    overall_confidence,
                    retrieval_stats['confidence_score'],
                    grounding_score,
                    coherence_score
                )
            }

            logger.info(f"Response confidence calculated: {overall_confidence:.3f} ({confidence_level})")
            return result

        except Exception as e:
            logger.error(f"Error calculating response confidence: {str(e)}")
            return {
                'overall_confidence': 0.0,
                'retrieval_confidence': 0.0,
                'content_grounding_score': 0.0,
                'response_coherence_score': 0.0,
                'confidence_level': 'very_low',
                'retrieval_quality': 'very_low',
                'is_confident': False,
                'confidence_explanation': 'Error occurred during confidence calculation'
            }

    def _calculate_content_grounding_score(self, response: str, retrieved_results: List[RetrievalResult]) -> float:
        """Calculate how well the response is grounded in the retrieved content"""
        if not retrieved_results:
            return 0.0

        try:
            # Calculate embedding similarity between response and retrieved content
            response_embedding = self.embedding_service.generate_embedding(response)
            content_similarities = []

            for result in retrieved_results:
                if result.is_relevant:  # Only consider relevant results
                    content_embedding = self.embedding_service.generate_embedding(result.content[:1000])

                    import numpy as np
                    response_array = np.array(response_embedding)
                    content_array = np.array(content_embedding)

                    # Calculate cosine similarity
                    similarity = np.dot(response_array, content_array) / (
                        np.linalg.norm(response_array) * np.linalg.norm(content_array)
                    )
                    content_similarities.append(float(similarity))

            if content_similarities:
                avg_similarity = sum(content_similarities) / len(content_similarities)
                return avg_similarity
            else:
                return 0.0

        except Exception as e:
            logger.warning(f"Error in content grounding calculation: {str(e)}")
            # Fallback: simple keyword overlap check
            response_words = set(response.lower().split()[:200])  # Limit for efficiency
            all_content = " ".join([r.content for r in retrieved_results if r.is_relevant])
            content_words = set(all_content.lower().split()[:500])

            overlap = response_words.intersection(content_words)
            return len(overlap) / len(response_words) if response_words else 0.0

    def _calculate_response_coherence(self, query: str, response: str) -> float:
        """Calculate how coherent and relevant the response is to the query"""
        try:
            query_embedding = self.embedding_service.generate_embedding(query)
            response_embedding = self.embedding_service.generate_embedding(response)

            import numpy as np
            query_array = np.array(query_embedding)
            response_array = np.array(response_embedding)

            # Calculate cosine similarity between query and response
            similarity = np.dot(query_array, response_array) / (
                np.linalg.norm(query_array) * np.linalg.norm(response_array)
            )

            return float(similarity)

        except Exception as e:
            logger.warning(f"Error in response coherence calculation: {str(e)}")
            # Fallback: basic overlap check
            query_words = set(query.lower().split())
            response_words = set(response.lower().split())
            overlap = query_words.intersection(response_words)
            return len(overlap) / len(query_words) if query_words else 0.0

    def _determine_response_confidence_level(self, confidence_score: float) -> str:
        """Determine confidence level based on score"""
        if confidence_score >= 0.8:
            return 'very_high'
        elif confidence_score >= 0.6:
            return 'high'
        elif confidence_score >= 0.4:
            return 'medium'
        elif confidence_score >= 0.2:
            return 'low'
        else:
            return 'very_low'

    def _explain_confidence(
        self,
        overall_confidence: float,
        retrieval_confidence: float,
        grounding_score: float,
        coherence_score: float
    ) -> str:
        """Provide explanation for the confidence score"""
        explanations = []

        if retrieval_confidence > 0.7:
            explanations.append("Strong retrieval results")
        elif retrieval_confidence > 0.5:
            explanations.append("Moderate retrieval quality")
        else:
            explanations.append("Weak retrieval results")

        if grounding_score > 0.6:
            explanations.append("Well-grounded in source content")
        elif grounding_score > 0.4:
            explanations.append("Somewhat grounded in source content")
        else:
            explanations.append("Poorly grounded in source content")

        if coherence_score > 0.5:
            explanations.append("Relevant to the query")
        else:
            explanations.append("May not be fully relevant to the query")

        return "; ".join(explanations)

# Example usage
if __name__ == "__main__":
    # Initialize service
    retrieval_service = RetrievalService()

    # Sample query
    query = "What is embodied intelligence?"

    # Perform retrieval
    results = retrieval_service.retrieve_content(query, limit=5)

    print(f"Retrieval results for '{query}':")
    for i, result in enumerate(results):
        print(f"{i+1}. Relevance: {result.relevance_score:.3f}, Semantic: {result.score:.3f}")
        print(f"   Content: {result.content[:100]}...")
        print(f"   Source: {result.source_file}")
        print(f"   Relevant: {result.is_relevant}")
        print()

    # Get statistics
    stats = retrieval_service.get_retrieval_statistics(results)
    print("Retrieval Statistics:")
    print(f"  Total results: {stats['total_results']}")
    print(f"  Avg relevance score: {stats['avg_relevance_score']:.3f}")
    print(f"  Relevant results: {stats['relevant_results']}")
    print(f"  Highly relevant results: {stats['highly_relevant_results']}")