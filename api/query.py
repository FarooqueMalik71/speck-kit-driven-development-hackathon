import os
import json
from typing import Dict, Any, List

# Import services (with error handling for missing dependencies)
try:
    from backend.src.services.retrieval_service import RetrievalService
    from backend.src.services.citation_service import CitationService
    from backend.src.services.confidence_fallback import FallbackService
    from backend.src.services.llm_service import LLMService
    from backend.src.config import settings
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Service import error: {e}")
    SERVICES_AVAILABLE = False

def handler(request):
    """Vercel API route handler for query endpoint"""
    # Handle CORS preflight request
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            },
            "body": json.dumps({})
        }

    # Only process POST requests
    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": "Method not allowed"})
        }

    try:
        # Parse the request body
        import json as json_lib
        body = json_lib.loads(request.body.decode('utf-8')) if request.body else {}
        query = body.get('query', '')
        context_ids = body.get('context_ids', [])
        mode = body.get('mode', 'full_book')

        # Check if services are available
        if not SERVICES_AVAILABLE:
            return {
                "statusCode": 503,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"detail": "AI services are not available due to missing dependencies"})
            }

        if not query:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"error": "Query is required"})
            }

        # Process the query
        retrieval_service = RetrievalService()

        # Retrieve relevant content based on query
        if mode == "selected_text" and context_ids:
            results = retrieval_service.retrieve_for_selected_text_qa(
                query, context_ids
            )
        else:
            results = retrieval_service.retrieve_content(query)

        # Generate response using LLM with retrieved context
        llm_service = LLMService(api_key=settings.gemini_api_key)

        llm_response = llm_service.generate_response_with_citations(
            query=query,
            context=results
        )
        answer = llm_response["answer"]

        # Generate citations
        citation_service = CitationService(retrieval_service)
        citations = citation_service.generate_citations(results)

        # Calculate confidence
        confidence_result = retrieval_service.calculate_response_confidence(
            query, results, answer
        )

        # Apply fallback if confidence is low
        fallback_service = FallbackService(retrieval_service)
        final_result = fallback_service.get_confidence_based_response(
            query, answer, results
        )

        # Apply content boundary enforcement
        boundary_check = retrieval_service.enforce_content_boundaries(
            query,
            [r.content for r in results],
            final_result['modified_response']
        )

        response_body = {
            "answer": final_result['modified_response'],
            "citations": [c['formatted_citation'] for c in citations],
            "confidence": confidence_result['overall_confidence'],
            "is_confident": confidence_result['is_confident'],
            "sources": [r.source_file for r in results],
            "boundary_compliance": boundary_check['boundary_compliance_score'],
            "needs_fact_check": boundary_check['needs_fact_check'],
            "session_id": body.get('session_id')  # Return session_id if provided
        }

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps(response_body)
        }

    except json_lib.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": "Invalid JSON in request body"})
        }
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"detail": f"Error processing query: {str(e)}"})
        }

# Export the handler for Vercel
def main(request):
    return handler(request)