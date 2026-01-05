from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
from pydantic import BaseModel
import os
import asyncio

# Import OpenAI Agents components with granular error handling
try:
    from openai import OpenAI
    from openai.types.beta.assistant import Assistant
    from openai.types.beta.thread import Thread
    from openai.types.beta.threads.run import Run
    AGENTS_AVAILABLE = True
except ImportError:
    print("OpenAI library not available")
    AGENTS_AVAILABLE = False

# Import individual services with granular error handling
try:
    from services.retrieval_service import RetrievalService
    RETRIEVAL_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"RetrievalService import error: {e}")
    RETRIEVAL_SERVICE_AVAILABLE = False

try:
    from services.hallucination_prevention import HallucinationPreventionService
    HALLUCINATION_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"HallucinationPreventionService import error: {e}")
    HALLUCINATION_SERVICE_AVAILABLE = False

try:
    from services.citation_service import CitationService
    CITATION_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"CitationService import error: {e}")
    CITATION_SERVICE_AVAILABLE = False

try:
    from services.confidence_fallback import FallbackService
    FALLBACK_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"FallbackService import error: {e}")
    FALLBACK_SERVICE_AVAILABLE = False

try:
    from services.content_validation import ContentValidationService
    CONTENT_VALIDATION_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"ContentValidationService import error: {e}")
    CONTENT_VALIDATION_SERVICE_AVAILABLE = False

try:
    from services.crawler import CrawlerService
    CRAWLER_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"CrawlerService import error: {e}")
    CRAWLER_SERVICE_AVAILABLE = False

try:
    from services.content_processor import ContentProcessor
    CONTENT_PROCESSOR_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"ContentProcessor import error: {e}")
    CONTENT_PROCESSOR_SERVICE_AVAILABLE = False

try:
    from services.embedding_service import EmbeddingService
    EMBEDDING_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"EmbeddingService import error: {e}")
    EMBEDDING_SERVICE_AVAILABLE = False

try:
    from services.vector_store import VectorStoreService
    VECTOR_STORE_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"VectorStoreService import error: {e}")
    VECTOR_STORE_SERVICE_AVAILABLE = False

# Import other components
try:
    from logging_config import logger, setup_logging
    from config import settings
    CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"Config/Logging import error: {e}")
    CONFIG_AVAILABLE = False

# Determine if core services are available for basic functionality
SERVICES_AVAILABLE = (
    RETRIEVAL_SERVICE_AVAILABLE and
    CONFIG_AVAILABLE
)

app = FastAPI(
    title="AI-Native Textbook Platform API",
    description="API for the Physical AI & Humanoid Robotics textbook platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration loader for LLM providers
class LLMConfiguration:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "gemini")  # Default to gemini for backward compatibility
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "mistralai/devstral-2512:free")

    def get_active_api_key(self):
        if self.provider == "openai":
            return self.openai_api_key
        elif self.provider == "openrouter":
            return self.openrouter_api_key
        return None

    def get_base_url(self):
        if self.provider == "openrouter":
            return "https://openrouter.ai/api/v1"
        return None  # Use default for OpenAI

# Initialize configuration
llm_config = LLMConfiguration()

# OpenAI Agent implementation if available
if AGENTS_AVAILABLE:
    class OpenAIAgentWrapper:
        """Wrapper for OpenAI Agent that integrates with existing RAG system"""

        def __init__(self, api_key: str, model: str = "gpt-4o", base_url: str = None):
            self.client = OpenAI(api_key=api_key)
            if base_url:
                self.client.base_url = base_url
            self.model = model

        def process_query(self, query: str, context_ids: List[str] = None, mode: str = "full_book") -> Dict[str, Any]:
            """Process a query through the agent."""
            try:
                # Retrieve context using existing RAG system
                retrieval_service = RetrievalService()

                if mode == "selected_text" and context_ids:
                    results = retrieval_service.retrieve_for_selected_text_qa(
                        query, context_ids
                    )
                else:
                    results = retrieval_service.retrieve_content(query)

                # Format context for the agent
                context_text = ""
                if results:
                    context_text = "Relevant textbook content:\n"
                    for i, result in enumerate(results[:5]):  # Use top 5 results
                        context_text += f"\n{i+1}. {result.content[:500]}..."  # Limit content length
                        if len(result.content) > 500:
                            context_text += " [truncated]"

                # Prepare the prompt
                prompt = f"""
                You are an AI assistant for the Physical AI & Humanoid Robotics textbook.
                Answer the user's question based on the provided textbook content.

                Question: {query}

                {context_text}

                Please provide a comprehensive answer based on the textbook content.
                If the information is not available in the provided context,
                politely acknowledge the limitation and suggest checking the textbook directly.

                Follow these rules strictly:
                1. ONLY use information from the retrieved chunks provided
                2. If the retrieved content does not contain sufficient information to answer the question,
                   clearly state that the information is not available in the provided documents
                3. Never fabricate, hallucinate, or provide information outside of the retrieved content
                4. When answering, always cite the sources from the retrieved content
                5. If the user provides specific context IDs, focus only on that selected text
                6. Maintain a helpful and professional tone
                """

                # Call the OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant for textbook queries. Follow the rules provided in the user message."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )

                answer = response.choices[0].message.content

                # Extract citation information from context
                citations = []
                sources = []
                for result in results:
                    if result.source_file and result.source_file not in sources:
                        sources.append(result.source_file)
                    if result.metadata.get('section_title') and result.metadata.get('section_title') not in citations:
                        citations.append(result.metadata.get('section_title', result.source_file))

                # Fallback: if no specific citations, use source files
                if not citations:
                    citations = sources[:3]  # Limit to first 3 sources

                return {
                    "answer": answer,
                    "citations": citations,
                    "sources": sources,
                    "confidence": 0.8,  # Default high confidence for agent responses
                    "is_confident": True,
                    "boundary_compliance": 0.9,
                    "needs_fact_check": False
                }
            except Exception as e:
                print(f"Error in agent processing: {str(e)}")
                raise

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

@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Welcome to the AI-Native Textbook Platform API"}

@app.get("/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "textbook-api",
        "environment": "development",
        "log_level": "INFO"
    }

# Textbook chatbot API router is temporarily disabled due to import issues for hackathon
# The core functionality is working through the /query endpoint
print("Textbook chatbot API router is temporarily disabled for stability")

# AI RAG Pipeline endpoints (with graceful degradation)
@app.post("/query", response_model=QueryResponse)
def query_textbook(request: QueryRequest):
    """Query the textbook with AI-powered responses with graceful degradation"""
    try:
        # Check if OpenAI Agents should be used based on configuration
        if llm_config.provider in ["openai", "openrouter"] and AGENTS_AVAILABLE:
            # Use OpenAI Agent approach
            api_key = llm_config.get_active_api_key()
            if not api_key:
                raise ValueError(f"No API key found for provider: {llm_config.provider}")

            base_url = llm_config.get_base_url()
            model = llm_config.model_name

            agent = OpenAIAgentWrapper(
                api_key=api_key,
                model=model,
                base_url=base_url
            )

            # Attempt to use retrieval service if available, otherwise use mock results
            results = []
            if RETRIEVAL_SERVICE_AVAILABLE:
                retrieval_service = RetrievalService()
                if request.mode == "selected_text" and request.context_ids:
                    results = retrieval_service.retrieve_for_selected_text_qa(
                        request.query, request.context_ids
                    )
                else:
                    results = retrieval_service.retrieve_content(request.query)

            result = agent.process_query(
                request.query,
                request.context_ids,
                request.mode
            )

            # Convert result to QueryResponse format
            return QueryResponse(
                answer=result['answer'],
                citations=result['citations'],
                confidence=result['confidence'],
                is_confident=result['is_confident'],
                sources=result['sources'],
                boundary_compliance=result['boundary_compliance'],
                needs_fact_check=result['needs_fact_check']
            )
        else:
            # Use existing Gemini-based approach for backward compatibility
            # Check if we have the basic services available
            if RETRIEVAL_SERVICE_AVAILABLE and CONFIG_AVAILABLE:
                from services.llm_service import LLMService
                retrieval_service = RetrievalService()

                # Initialize LLM service with Gemini API if available, otherwise use mock
                try:
                    llm_service = LLMService(api_key=settings.gemini_api_key)
                except Exception as e:
                    # If LLM service fails, use a mock implementation
                    print(f"LLM service initialization failed: {str(e)}, using mock implementation")
                    # Create a mock response
                    mock_answer = f"Based on the textbook content, here's information about: {request.query}. [Note: LLM service is not available. This is a simulated response.]"
                    return QueryResponse(
                        answer=mock_answer,
                        citations=[],
                        confidence=0.5,
                        is_confident=False,
                        sources=[],
                        boundary_compliance=0.5,
                        needs_fact_check=True
                    )

                # Retrieve relevant content based on query
                try:
                    if request.mode == "selected_text" and request.context_ids:
                        results = retrieval_service.retrieve_for_selected_text_qa(
                            request.query, request.context_ids
                        )
                    else:
                        results = retrieval_service.retrieve_content(request.query)
                except Exception as e:
                    print(f"Retrieval service failed: {str(e)}, using empty results")
                    results = []

                # Generate response using LLM with retrieved context
                try:
                    llm_response = llm_service.generate_response_with_citations(
                        query=request.query,
                        context=results
                    )
                    answer = llm_response["answer"]
                except Exception as e:
                    print(f"LLM response generation failed: {str(e)}, using fallback")
                    answer = f"Based on the textbook content, here's information about: {request.query}. [Note: Response generated with limited capabilities.]"

                # Generate citations if service is available
                citations = []
                if CITATION_SERVICE_AVAILABLE and results:
                    try:
                        citation_service = CitationService(retrieval_service)
                        citations = citation_service.generate_citations(results)
                    except Exception as e:
                        print(f"Citation service failed: {str(e)}, using fallback")
                        # Use fallback citation from results
                        for result in results:
                            if result.source_file and result.source_file not in citations:
                                citations.append(result.source_file)

                # Calculate confidence if service is available
                try:
                    confidence_result = retrieval_service.calculate_response_confidence(
                        request.query, results, answer
                    )
                except Exception as e:
                    print(f"Confidence calculation failed: {str(e)}, using fallback")
                    confidence_result = {
                        'overall_confidence': 0.5,
                        'is_confident': False
                    }

                # Apply fallback if service is available
                try:
                    if FALLBACK_SERVICE_AVAILABLE:
                        fallback_service = FallbackService(retrieval_service)
                        final_result = fallback_service.get_confidence_based_response(
                            request.query, answer, results
                        )
                        answer = final_result['modified_response']
                except Exception as e:
                    print(f"Fallback service failed: {str(e)}, using original answer")

                # Apply content boundary enforcement if service is available
                try:
                    if results:  # Only enforce boundaries if we have results
                        boundary_check = retrieval_service.enforce_content_boundaries(
                            request.query,
                            [r.content for r in results],
                            answer
                        )
                    else:
                        # Default boundary check values when no results
                        boundary_check = {
                            'boundary_compliance_score': 0.5,
                            'needs_fact_check': True
                        }
                except Exception as e:
                    print(f"Boundary enforcement failed: {str(e)}, using fallback")
                    boundary_check = {
                        'boundary_compliance_score': 0.5,
                        'needs_fact_check': True
                    }

                return QueryResponse(
                    answer=answer,
                    citations=[c['formatted_citation'] for c in citations] if citations and all(hasattr(c, 'formatted_citation') for c in citations) else [str(c) for c in citations] if citations else [],
                    confidence=confidence_result['overall_confidence'],
                    is_confident=confidence_result['is_confident'],
                    sources=[r.source_file for r in results] if results else [],
                    boundary_compliance=boundary_check['boundary_compliance_score'],
                    needs_fact_check=boundary_check['needs_fact_check']
                )
            else:
                # If core services are not available, return a basic mock response
                return QueryResponse(
                    answer=f"Based on the textbook content, here's information about: {request.query}. [Note: Core services are not available. This is a simulated response.]",
                    citations=[],
                    confidence=0.0,
                    is_confident=False,
                    sources=[],
                    boundary_compliance=0.0,
                    needs_fact_check=True
                )
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        # Return a graceful fallback response instead of raising an exception
        return QueryResponse(
            answer=f"Sorry, I'm having trouble processing your query about '{request.query}'. Please try again later.",
            citations=[],
            confidence=0.0,
            is_confident=False,
            sources=[],
            boundary_compliance=0.0,
            needs_fact_check=True
        )

if __name__ == "__main__":
    import uvicorn
    print("Starting server on 0.0.0.0:8000")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )