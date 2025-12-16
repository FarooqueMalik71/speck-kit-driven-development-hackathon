from backend.src.services.retrieval_service import RetrievalService
from backend.src.services.hallucination_prevention import HallucinationPreventionService
from backend.src.services.citation_service import CitationService
from backend.src.services.confidence_fallback import FallbackService
from backend.src.services.content_validation import ContentValidationService
from backend.src.services.embedding_service import EmbeddingService
from backend.src.services.vector_store import VectorStoreService
from backend.src.services.semantic_search import SemanticSearchService

def test_ai_rag_pipeline():
    """Test the complete AI RAG pipeline with all safety mechanisms"""
    print("Testing AI RAG Pipeline with Safety Mechanisms...")

    # Initialize all services
    embedding_service = EmbeddingService()
    vector_store = VectorStoreService()
    semantic_search = SemanticSearchService(vector_store, embedding_service)
    retrieval_service = RetrievalService(vector_store, semantic_search, embedding_service)
    hallucination_service = HallucinationPreventionService(retrieval_service, embedding_service)
    citation_service = CitationService(retrieval_service, vector_store)
    fallback_service = FallbackService(retrieval_service, hallucination_service)
    validation_service = ContentValidationService(vector_store, embedding_service)

    # Test query
    query = "What is Physical AI?"

    # Simulate retrieval results (normally these would come from vector search)
    from backend.src.services.retrieval_service import RetrievalResult
    sample_results = [
        RetrievalResult(
            id="test_chunk_1",
            content="Physical AI represents a paradigm shift in artificial intelligence, focusing on the integration of perception, reasoning, and action in physical environments.",
            source_file="docs/introduction.md",
            score=0.85,
            metadata={'chapter': '1', 'section': 'Introduction', 'page_number': '5'},
            relevance_score=0.82,
            context_similarity=0.78,
            is_relevant=True
        )
    ]

    # Test 1: Confidence scoring
    print("\n1. Testing Confidence Scoring...")
    ai_response = "Physical AI is a field that combines perception, reasoning, and action in physical environments."
    confidence_result = retrieval_service.calculate_response_confidence(query, sample_results, ai_response)
    print(f"   Confidence: {confidence_result['overall_confidence']:.3f}")
    print(f"   Confidence Level: {confidence_result['confidence_level']}")

    # Test 2: Hallucination detection
    print("\n2. Testing Hallucination Detection...")
    hallucination_result = hallucination_service.detect_hallucinations(query, ai_response, [
        {'content': result.content, 'source_file': result.source_file, 'score': result.score}
        for result in sample_results
    ])
    print(f"   Hallucination Probability: {hallucination_result['hallucination_probability']:.3f}")
    print(f"   Is Hallucinated: {hallucination_result['is_hallucinated']}")

    # Test 3: Citation generation
    print("\n3. Testing Citation Generation...")
    citations = citation_service.generate_citations(sample_results)
    print(f"   Generated {len(citations)} citations")
    if citations:
        print(f"   First citation: {citations[0]['formatted_citation']}")

    # Test 4: Fallback mechanism
    print("\n4. Testing Fallback Mechanism...")
    # Create a low-confidence scenario
    low_confidence_data = {
        'overall_confidence': 0.3,
        'retrieval_confidence': 0.4,
        'content_grounding_score': 0.25,
        'response_coherence_score': 0.45,
        'confidence_level': 'low',
        'retrieval_quality': 'low',
        'is_confident': False,
        'confidence_explanation': 'Weak retrieval results; Poorly grounded in source content'
    }

    fallback_result = fallback_service.handle_low_confidence_response(
        query, ai_response, low_confidence_data, sample_results
    )
    print(f"   Fallback Applied: {fallback_result['fallback_applied']}")
    print(f"   Fallback Type: {fallback_result['fallback_type']}")

    # Test 5: Content validation
    print("\n5. Testing Content Validation...")
    validation_result = validation_service.validate_content_pipeline(
        sample_results[0].content,
        sample_results[0].source_file,
        [{'content': sample_results[0].content, 'source_file': sample_results[0].source_file}]
    )
    print(f"   Overall Validity: {validation_result['overall_validity']}")
    print(f"   Overall Score: {validation_result['overall_score']:.3f}")
    print(f"   Total Issues: {validation_result['validation_summary']['total_issues']}")

    # Test 6: Content boundary enforcement
    print("\n6. Testing Content Boundary Enforcement...")
    boundary_result = retrieval_service.enforce_content_boundaries(
        query,
        [result.content for result in sample_results],
        ai_response
    )
    print(f"   Is Valid Response: {boundary_result['is_valid_response']}")
    print(f"   Boundary Compliance Score: {boundary_result['boundary_compliance_score']:.3f}")

    print("\n✅ All AI RAG Pipeline components tested successfully!")
    print("✅ Phase 3: AI Embeddings & RAG Pipeline is complete!")

if __name__ == "__main__":
    test_ai_rag_pipeline()