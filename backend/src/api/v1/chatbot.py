from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
import uuid
import logging

from models.query_models import QueryRequest, QueryResponse
from services.conversation_service import ConversationService
from services.rag_service import RAGService
from services.citation_service import CitationService
from services.retrieval_service import RetrievalService
from services.llm_service import LLMService
from config import settings

logger = logging.getLogger(__name__)

# Initialize services
retrieval_service = RetrievalService()
citation_service = CitationService(retrieval_service)
llm_service = LLMService(api_key=settings.gemini_api_key)
rag_service = RAGService(retrieval_service, citation_service, llm_service)
conversation_service = ConversationService(session_ttl_hours=settings.session_ttl_hours)

router = APIRouter(tags=["chatbot"])

@router.post("/query", response_model=QueryResponse)
async def query_textbook(request: QueryRequest):
    """Query the textbook with AI-powered responses"""
    try:
        logger.info(f"Processing query: '{request.query[:50]}...' for session {request.session_id}")

        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        session = conversation_service.get_session(session_id)

        if not session:
            session = conversation_service.create_session()
            session_id = session.session_id

        # Process the query using RAG service
        textbook_response = rag_service.process_query(
            query=request.query,
            session_id=session_id,
            context_ids=request.context_ids,
            mode=request.mode
        )

        # Add the user query to the conversation history
        from ...models.conversation_turn import ConversationTurn
        user_turn = ConversationTurn(
            turn_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            role="user",
            content=request.query
        )
        conversation_service.add_turn_to_session(session_id, user_turn)

        # Add the assistant response to the conversation history
        assistant_turn = ConversationTurn(
            turn_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            role="assistant",
            content=textbook_response.content,
            references=textbook_response.references
        )
        conversation_service.add_turn_to_session(session_id, assistant_turn)

        # Convert to QueryResponse format
        response = QueryResponse(
            response_id=textbook_response.response_id,
            session_id=session_id,
            answer=textbook_response.content,
            citations=[ref.title for ref in textbook_response.references],
            confidence=textbook_response.confidence,
            is_confident=textbook_response.confidence > 0.6,
            sources=[ref.url for ref in textbook_response.references],
            boundary_compliance=0.9,  # Default high compliance for textbook responses
            needs_fact_check=textbook_response.confidence < 0.5,
            references=textbook_response.references,
            structured_content=textbook_response.structured_content
        )

        logger.info(f"Query processed successfully for session {session_id}")
        return response

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/session/{session_id}")
async def get_session_history(session_id: str):
    """Retrieve conversation history for a specific session"""
    try:
        logger.info(f"Retrieving session history for {session_id}")

        session = conversation_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Create response with session history
        history_response = {
            "sessionId": session.session_id,
            "createdAt": session.created_at.isoformat(),
            "lastAccessed": session.last_accessed.isoformat(),
            "expiresAt": session.expires_at.isoformat(),
            "history": [
                {
                    "turnId": turn.turn_id,
                    "timestamp": turn.timestamp.isoformat(),
                    "role": turn.role,
                    "content": turn.content,
                    "references": [ref.dict() for ref in turn.references]
                }
                for turn in session.history
            ]
        }

        logger.info(f"Session history retrieved for {session_id}")
        return history_response

    except Exception as e:
        logger.error(f"Error retrieving session history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving session history: {str(e)}")


@router.post("/session/{session_id}/clear")
async def clear_session_history(session_id: str):
    """Clear the conversation history for a specific session while keeping the session active"""
    try:
        logger.info(f"Clearing session history for {session_id}")

        success = conversation_service.clear_session_history(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "sessionId": session_id,
            "message": "Session history cleared successfully"
        }

    except Exception as e:
        logger.error(f"Error clearing session history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing session history: {str(e)}")


@router.get("/capabilities")
async def get_capabilities():
    """Retrieve the capabilities and configuration of the textbook RAG chatbot"""
    try:
        logger.info("Retrieving capabilities")

        capabilities_response = {
            "capabilities": {
                "structuredResponses": True,
                "conversationHistory": True,
                "referenceAttachment": True,
                "politeLanguageHandling": True,
                "academicTone": True,
                "contextAwareness": True
            },
            "configuration": {
                "maxHistoryLength": settings.max_history_turns,
                "maxResponseLength": settings.max_response_length,
                "referenceSources": ["internal", "external"],
                "supportedModes": ["full_book", "selected_text"],
                "academicToneEnforced": settings.academic_tone_enforcement,
                "referenceRequired": settings.reference_required,
                "politeLanguageHandling": settings.polite_language_handling
            }
        }

        logger.info("Capabilities retrieved successfully")
        return capabilities_response

    except Exception as e:
        logger.error(f"Error retrieving capabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving capabilities: {str(e)}")


# Additional endpoint for handling ambiguous queries if needed
@router.post("/handle-ambiguous-query")
async def handle_ambiguous_query(query: str):
    """Handle queries that are ambiguous or unclear"""
    try:
        logger.info(f"Handling ambiguous query: '{query[:50]}...'")

        # Use RAG service to handle ambiguous query
        response = rag_service.handle_ambiguous_query(query)

        return {
            "responseId": response.response_id,
            "answer": response.content,
            "confidence": response.confidence,
            "is_confident": response.confidence > 0.6
        }

    except Exception as e:
        logger.error(f"Error handling ambiguous query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error handling ambiguous query: {str(e)}")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for the chatbot API"""
    return {
        "status": "healthy",
        "service": "textbook-chatbot-api",
        "timestamp": datetime.now().isoformat()
    }