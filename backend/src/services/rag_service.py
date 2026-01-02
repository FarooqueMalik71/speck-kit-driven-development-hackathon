from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from ..models.academic_query import AcademicQuery
from ..models.textbook_response import TextbookResponse
from ..models.structured_content import StructuredContent
from ..models.definition import Definition
from ..models.example import Example
from ..models.reference import Reference
from .retrieval_service import RetrievalService
from .citation_service import CitationService
from .llm_service import LLMService
from .retrieval_service import RetrievalResult


class RAGService:
    """
    Service for RAG (Retrieval-Augmented Generation) with textbook formatting
    """

    def __init__(self, retrieval_service: RetrievalService, citation_service: CitationService, llm_service: LLMService):
        self.retrieval_service = retrieval_service
        self.citation_service = citation_service
        self.llm_service = llm_service

    def process_query(
        self,
        query: str,
        session_id: str,
        context_ids: List[str] = None,
        mode: str = "full_book"
    ) -> TextbookResponse:
        """
        Process an academic query and return a textbook-style response
        """
        # Retrieve relevant content based on query
        if mode == "selected_text" and context_ids:
            results = self.retrieval_service.retrieve_for_selected_text_qa(query, context_ids)
        else:
            results = self.retrieval_service.retrieve_content(query)

        # Generate response using LLM with retrieved context
        llm_response = self.llm_service.generate_response_with_citations(
            query=query,
            context=results
        )
        answer = llm_response["answer"]

        # Generate citations
        citations = self.citation_service.generate_citations(results)

        # Calculate confidence
        confidence_result = self.retrieval_service.calculate_response_confidence(query, results, answer)

        # Format response as textbook-style
        textbook_response = self._format_textbook_response(
            query=query,
            answer=answer,
            results=results,
            citations=citations,
            confidence_result=confidence_result
        )

        # Create TextbookResponse object
        response = TextbookResponse(
            response_id=str(uuid.uuid4()),
            query_id=str(uuid.uuid4()),  # In a real implementation, you'd pass this from the query
            session_id=session_id,
            content=textbook_response["answer"],
            structured_content=textbook_response["structured_content"],
            references=textbook_response["references"],
            timestamp=datetime.now(),
            confidence=confidence_result['overall_confidence'],
            is_contextual=False  # This would be set based on conversation history
        )

        return response

    def _format_textbook_response(
        self,
        query: str,
        answer: str,
        results: List[RetrievalResult],
        citations: List[Dict],
        confidence_result: Dict
    ) -> Dict[str, Any]:
        """
        Format the response in textbook style with structured content
        """
        # Extract structured elements from the answer
        structured_content = self._extract_structured_content(answer)

        # Generate references from citations
        references = self._generate_references(citations, results)

        # Check if the query was not found in knowledge base
        if "not available in the current knowledge base" in answer.lower():
            # Format as polite fallback response
            formatted_answer = f"The requested information is not available in the current knowledge base."
        else:
            # Apply textbook formatting
            formatted_answer = self._apply_textbook_formatting(answer)

        return {
            "answer": formatted_answer,
            "structured_content": structured_content,
            "references": references
        }

    def _extract_structured_content(self, answer: str) -> StructuredContent:
        """
        Extract structured content (headings, bullet points, definitions, examples) from answer
        """
        # This is a simplified implementation - in a real system, this would use NLP
        # to identify and extract structured elements from the response
        headings = []
        bullet_points = []
        definitions = []
        examples = []

        # Simple heuristic-based extraction
        lines = answer.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                headings.append(line.lstrip('# ').strip())
            elif line.startswith('- ') or line.startswith('* '):
                bullet_points.append(line[2:].strip())
            elif ':' in line and 'definition' in line.lower():
                # Simple definition detection
                parts = line.split(':', 1)
                if len(parts) > 1:
                    definitions.append(Definition(
                        term=parts[0].replace('definition', '').strip(),
                        definition=parts[1].strip()
                    ))

        return StructuredContent(
            headings=headings,
            bullet_points=bullet_points,
            definitions=definitions,
            examples=examples
        )

    def _generate_references(self, citations: List[Dict], results: List[RetrievalResult]) -> List[Reference]:
        """
        Generate reference objects from citations and results
        """
        references = []

        # Convert citations to Reference objects
        for citation in citations:
            if citation.get('formatted_citation'):
                references.append(Reference(
                    type="internal",
                    title=citation.get('title', 'Reference'),
                    url=citation.get('url', '#'),
                    description=citation.get('formatted_citation', ''),
                    relevance=0.8  # Default relevance
                ))

        # Add references from results if not already included
        for result in results:
            if hasattr(result, 'source_file') and result.source_file:
                # Check if this source is already in references
                if not any(ref.url == result.source_file for ref in references):
                    references.append(Reference(
                        type="internal",
                        title=f"Source: {result.source_file}",
                        url=result.source_file,
                        description=f"Source document: {result.source_file}",
                        relevance=0.7
                    ))

        return references

    def _apply_textbook_formatting(self, answer: str) -> str:
        """
        Apply textbook-style formatting to the answer
        """
        # This is a simplified implementation - in a real system, this would use
        # more sophisticated formatting based on academic standards
        formatted_answer = answer

        # Ensure proper academic tone by removing casual language
        formatted_answer = self._enforce_academic_tone(formatted_answer)

        # Add further reading section if not present but there are results
        if "📘 Further Reading" not in formatted_answer and "Further Reading" not in formatted_answer:
            formatted_answer += "\n\n📘 **Further Reading / Reference**\n- See the references section for additional resources."

        return formatted_answer

    def _enforce_academic_tone(self, text: str) -> str:
        """
        Enforce academic tone by replacing casual phrases with formal ones
        """
        # Replace casual AI phrases
        replacements = {
            "as an AI model": "according to the textbook",
            "as an AI assistant": "according to the textbook",
            "as an artificial intelligence": "according to the textbook",
            "AI model": "textbook definition",
            "AI system": "textbook system",
            "I think": "The evidence suggests",
            "I believe": "The evidence suggests",
            "I feel": "The evidence indicates",
            "in my opinion": "according to available information",
            "just": "",  # Remove casual intensifiers
            "basically": "fundamentally",
            "actually": "",  # Remove casual intensifiers
            "really": "",  # Remove casual intensifiers
            "kind of": "somewhat",
            "sort of": "to some extent",
            "a bit": "slightly",
        }

        result = text
        for old, new in replacements.items():
            if new:
                result = result.replace(old, new)
            else:
                # When replacement is empty string, remove the phrase
                result = result.replace(old, new)

        # Ensure proper academic structure
        result = self._ensure_academic_structure(result)

        return result

    def _ensure_academic_structure(self, text: str) -> str:
        """
        Ensure the response follows academic structure with proper formatting
        """
        # Add proper headings if missing
        lines = text.split('\n')
        processed_lines = []

        for line in lines:
            stripped_line = line.strip()
            if stripped_line:
                # Add structure to key concepts
                processed_lines.append(line)
            else:
                processed_lines.append(line)

        result = '\n'.join(processed_lines)

        # Ensure proper academic conclusion
        if not any(phrase in result.lower() for phrase in ['conclusion', 'summary', 'therefore', 'thus', 'hence']):
            # Add academic closure if appropriate
            pass  # For now, we'll leave as is

        return result

    def handle_ambiguous_query(self, query: str) -> TextbookResponse:
        """
        Handle queries that are ambiguous or unclear
        """
        # Create a response that politely clarifies the intent
        clarification_answer = f"I understand your intent. Allow me to clarify it accurately.\n\n{query}"

        response = TextbookResponse(
            response_id=str(uuid.uuid4()),
            query_id=str(uuid.uuid4()),
            session_id="",  # This would be passed in a real implementation
            content=clarification_answer,
            structured_content=StructuredContent(),
            references=[],
            timestamp=datetime.now(),
            confidence=0.5,  # Lower confidence for clarification responses
            is_contextual=False
        )

        return response