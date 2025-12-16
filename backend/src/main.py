from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
from pydantic import BaseModel
from .config import settings
from .logging_config import logger

app = FastAPI(
    title="AI-Native Textbook Platform API",
    description="API for the Physical AI & Humanoid Robotics textbook platform",
    version="1.0.0",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import services (with error handling for missing dependencies)
try:
    from .services.retrieval_service import RetrievalService, RetrievalResult
    from .services.hallucination_prevention import HallucinationPreventionService
    from .services.citation_service import CitationService
    from .services.confidence_fallback import FallbackService
    from .services.content_validation import ContentValidationService
    SERVICES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some services not available due to missing dependencies: {e}")
    SERVICES_AVAILABLE = False

# Request/response models
class QueryRequest(BaseModel):
    query: str
    context_ids: List[str] = []
    mode: str = "full_book"  # "full_book" or "selected_text"

class QueryResponse(BaseModel):
    answer: str
    citations: List[str] = []
    confidence: float = 0.0
    is_confident: bool = False
    sources: List[str] = []
    boundary_compliance: float = 0.0
    needs_fact_check: bool = False

class ValidateContentRequest(BaseModel):
    content: str
    source_file: str
    expected_topics: List[str] = []

class ValidateContentResponse(BaseModel):
    is_valid: bool
    overall_score: float
    integrity_score: float
    quality_score: float
    consistency_score: float
    issues: List[str]

@app.get("/")
def read_root() -> Dict[str, str]:
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the AI-Native Textbook Platform API"}

@app.get("/health")
def health_check() -> Dict[str, Any]:
    logger.info("Health check endpoint accessed")
    return {
        "status": "healthy",
        "service": "textbook-api",
        "environment": settings.environment,
        "debug": settings.debug
    }

# AI RAG Pipeline endpoints (only if services are available)
if SERVICES_AVAILABLE:
    @app.post("/query", response_model=QueryResponse)
    def query_textbook(request: QueryRequest):
        """Query the textbook with AI-powered responses"""
        logger.info(f"Processing query: {request.query[:50]}...")

        try:
            # Initialize services
            retrieval_service = RetrievalService()

            # Retrieve relevant content based on query
            if request.mode == "selected_text" and request.context_ids:
                results = retrieval_service.retrieve_for_selected_text_qa(
                    request.query, request.context_ids
                )
            else:
                results = retrieval_service.retrieve_content(request.query)

            # Generate a simulated response (in a real implementation, this would connect to an LLM)
            answer = f"Based on the textbook content, here's information about: {request.query}"

            # Generate citations
            citation_service = CitationService(retrieval_service)
            citations = citation_service.generate_citations(results)

            # Calculate confidence
            confidence_result = retrieval_service.calculate_response_confidence(
                request.query, results, answer
            )

            # Apply fallback if confidence is low
            fallback_service = FallbackService(retrieval_service)
            final_result = fallback_service.get_confidence_based_response(
                request.query, answer, results
            )

            # Apply content boundary enforcement
            boundary_check = retrieval_service.enforce_content_boundaries(
                request.query,
                [r.content for r in results],
                final_result['modified_response']
            )

            return QueryResponse(
                answer=final_result['modified_response'],
                citations=[c['formatted_citation'] for c in citations],
                confidence=confidence_result['overall_confidence'],
                is_confident=confidence_result['is_confident'],
                sources=[r.source_file for r in results],
                boundary_compliance=boundary_check['boundary_compliance_score'],
                needs_fact_check=boundary_check['needs_fact_check']
            )
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

    @app.post("/validate-content", response_model=ValidateContentResponse)
    def validate_content(request: ValidateContentRequest):
        """Validate content quality and integrity"""
        logger.info(f"Validating content for: {request.source_file}")

        try:
            validation_service = ContentValidationService()
            result = validation_service.validate_content_pipeline(
                request.content,
                request.source_file,
                expected_topics=request.expected_topics
            )

            return ValidateContentResponse(
                is_valid=result['overall_validity'],
                overall_score=result['overall_score'],
                integrity_score=result['integrity_validation']['quality_score'],
                quality_score=result['quality_validation']['quality_score'],
                consistency_score=result['consistency_validation']['consistency_score'],
                issues=result['validation_summary']['critical_issues'] + result['validation_summary']['warning_issues']
            )
        except Exception as e:
            logger.error(f"Error validating content: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error validating content: {str(e)}")

    @app.post("/check-hallucinations")
    def check_hallucinations(query: str, response: str, context: List[Dict[str, str]]):
        """Check for hallucinations in AI responses"""
        try:
            hallucination_service = HallucinationPreventionService()
            retrieved_context = [{'content': item.get('content', ''), 'source_file': item.get('source_file', '')} for item in context]
            result = hallucination_service.detect_hallucinations(query, response, retrieved_context)
            return result
        except Exception as e:
            logger.error(f"Error checking hallucinations: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error checking hallucinations: {str(e)}")

else:
    @app.post("/query")
    def query_textbook_unavailable(request: QueryRequest):
        raise HTTPException(status_code=503, detail="AI services are not available due to missing dependencies")

    @app.post("/validate-content")
    def validate_content_unavailable(request: ValidateContentRequest):
        raise HTTPException(status_code=503, detail="Content validation services are not available due to missing dependencies")

# Placeholder for future API endpoints
# The actual implementation will be added in subsequent tasks

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server on 0.0.0.0:8000")
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )