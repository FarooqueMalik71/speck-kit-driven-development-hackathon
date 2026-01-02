from typing import List, Dict, Any, Optional
import logging
from .retrieval_service import RetrievalService, RetrievalResult
from .vector_store import VectorStoreService

logger = logging.getLogger(__name__)

class CitationService:
    """Service for generating citations for AI responses based on retrieved content"""

    def __init__(self, retrieval_service: RetrievalService = None, vector_store: VectorStoreService = None):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.vector_store = vector_store or VectorStoreService()

    def generate_citations(self, retrieval_results: List[RetrievalResult], max_citations: int = 5) -> List[Dict[str, Any]]:
        """Generate citations for the retrieved results used in AI response"""
        logger.info(f"Generating citations for {len(retrieval_results)} retrieval results")

        citations = []
        for result in retrieval_results[:max_citations]:
            citation = self._format_citation(result)
            citations.append(citation)

        logger.info(f"Generated {len(citations)} citations")
        return citations

    def _format_citation(self, result: RetrievalResult) -> Dict[str, Any]:
        """Format a single citation from retrieval result"""
        # Extract chapter/section information from metadata if available
        chapter = result.metadata.get('chapter', 'Unknown')
        section = result.metadata.get('section', 'Unknown')
        page_number = result.metadata.get('page_number', 'N/A')

        # Create citation in textbook format
        citation = {
            'id': result.id,
            'source_file': result.source_file,
            'chapter': chapter,
            'section': section,
            'page_number': page_number,
            'content_preview': result.content[:200] + "..." if len(result.content) > 200 else result.content,
            'relevance_score': result.relevance_score,
            'formatted_citation': self._create_formatted_citation(result),
            'url': self._generate_source_url(result.source_file, result.metadata),
            'confidence': self._calculate_citation_confidence(result)
        }

        return citation

    def _create_formatted_citation(self, result: RetrievalResult) -> str:
        """Create a properly formatted citation string"""
        # Extract information from metadata
        chapter = result.metadata.get('chapter', 'N/A')
        section = result.metadata.get('section', 'N/A')
        page_number = result.metadata.get('page_number', 'N/A')

        # Get filename without extension
        import os
        filename = os.path.splitext(os.path.basename(result.source_file))[0]

        # Format: Chapter X, Section Y, Page Z, File: filename
        formatted = f"Chapter {chapter}, Section {section}, Page {page_number}, File: {filename}"
        return formatted

    def _generate_source_url(self, source_file: str, metadata: Dict[str, Any]) -> Optional[str]:
        """Generate URL to the source in the textbook"""
        try:
            # Convert file path to URL-friendly format
            import os
            from urllib.parse import quote

            # Remove file extension and convert to URL path
            base_name = os.path.splitext(source_file)[0]
            url_path = base_name.replace('\\', '/').replace(' ', '_')

            # If we have section information, add it as an anchor
            section = metadata.get('section', '')
            if section:
                section_anchor = quote(section.replace(' ', '-').lower())
                return f"/textbook/{url_path}#{section_anchor}"
            else:
                return f"/textbook/{url_path}"

        except Exception as e:
            logger.warning(f"Error generating source URL: {str(e)}")
            return None

    def _calculate_citation_confidence(self, result: RetrievalResult) -> float:
        """Calculate confidence in the citation based on various factors"""
        # Combine multiple factors for confidence score
        relevance_factor = result.relevance_score
        semantic_factor = result.score  # Raw semantic score
        context_factor = result.context_similarity

        # Weighted average with emphasis on relevance
        confidence = (relevance_factor * 0.5) + (semantic_factor * 0.3) + (context_factor * 0.2)

        return min(max(confidence, 0.0), 1.0)  # Clamp between 0 and 1

    def create_citation_text(self, citations: List[Dict[str, Any]], style: str = "textbook") -> str:
        """Create formatted citation text in specified style"""
        if not citations:
            return ""

        if style == "textbook":
            return self._create_textbook_style_citation(citations)
        elif style == "academic":
            return self._create_academic_style_citation(citations)
        elif style == "inline":
            return self._create_inline_citation(citations)
        else:
            return self._create_textbook_style_citation(citations)

    def _create_textbook_style_citation(self, citations: List[Dict[str, Any]]) -> str:
        """Create textbook-style citation"""
        if len(citations) == 1:
            citation = citations[0]
            return f"Source: {citation['formatted_citation']}"
        else:
            citation_texts = []
            for i, citation in enumerate(citations):
                citation_texts.append(f"[{i+1}] {citation['formatted_citation']}")

            return f"Sources: {', '.join(citation_texts)}"

    def _create_academic_style_citation(self, citations: List[Dict[str, Any]]) -> str:
        """Create academic-style citation"""
        citation_texts = []
        for citation in citations:
            text = f"Physical AI Textbook, {citation['formatted_citation']}"
            if citation['url']:
                text += f" ({citation['url']})"
            citation_texts.append(text)

        return "References: " + "; ".join(citation_texts)

    def _create_inline_citation(self, citations: List[Dict[str, Any]]) -> str:
        """Create inline citation suitable for inclusion in response"""
        if not citations:
            return ""

        # For inline citations, just return a simple reference
        if len(citations) == 1:
            return f" (See: {citations[0]['formatted_citation']})"
        else:
            return f" (See: {len(citations)} sources in textbook)"

    def validate_citations(self, citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate citations and return quality metrics"""
        if not citations:
            return {
                'valid_citations': 0,
                'total_citations': 0,
                'avg_confidence': 0.0,
                'valid': True,
                'issues': ['No citations provided']
            }

        total_citations = len(citations)
        valid_citations = 0
        total_confidence = 0.0
        issues = []

        for citation in citations:
            is_valid = True

            # Check if required fields exist
            if not citation.get('id'):
                is_valid = False
                issues.append(f"Citation {citation.get('id', 'unknown')} missing ID")

            if not citation.get('source_file'):
                is_valid = False
                issues.append(f"Citation {citation.get('id', 'unknown')} missing source file")

            if citation.get('relevance_score', 0) < 0.3:
                issues.append(f"Citation {citation.get('id', 'unknown')} has low relevance score")

            if is_valid:
                valid_citations += 1
                total_confidence += citation.get('confidence', 0)

        avg_confidence = total_confidence / valid_citations if valid_citations > 0 else 0.0

        return {
            'valid_citations': valid_citations,
            'total_citations': total_citations,
            'avg_confidence': avg_confidence,
            'valid': valid_citations == total_citations,
            'issues': issues
        }

    def create_citation_for_response(self, query: str, response: str, retrieval_results: List[RetrievalResult]) -> Dict[str, Any]:
        """Create comprehensive citation information for an AI response"""
        logger.info(f"Creating citations for response to query: '{query[:50]}...'")

        # Generate citations
        citations = self.generate_citations(retrieval_results)

        # Validate citations
        validation = self.validate_citations(citations)

        # Create citation text for inclusion in response
        inline_citation = self.create_citation_text(citations, style="inline")

        # Format final result
        result = {
            'citations': citations,
            'validation': validation,
            'inline_citation': inline_citation,
            'citation_text': self.create_citation_text(citations, style="textbook"),
            'has_valid_sources': validation['valid'] and validation['valid_citations'] > 0,
            'confidence_in_sources': validation['avg_confidence'],
            'total_sources_used': len(citations)
        }

        logger.info(f"Citation creation complete: {len(citations)} citations, valid={result['has_valid_sources']}")
        return result

    def create_reference_section(self, results: List[RetrievalResult]) -> str:
        """Create a proper reference section for textbook responses"""
        if not results:
            return "📘 **Further Reading / Reference**\n- No references available for this query."

        reference_section = "📘 **Further Reading / Reference**\n"

        for i, result in enumerate(results, 1):
            section_title = result.metadata.get('section_title', 'Section')
            source_file = result.source_file
            description = result.content[:100] + "..." if len(result.content) > 100 else result.content

            reference_section += f"{i}. {section_title} - {source_file}\n"

        return reference_section

    def generate_textbook_references(self, results: List[RetrievalResult]) -> List[Dict[str, Any]]:
        """Generate proper textbook-style reference objects from results"""
        references = []

        for result in results:
            section_title = result.metadata.get('section_title', 'Section')
            source_file = result.source_file
            description = result.content[:200] + "..." if len(result.content) > 200 else result.content

            reference = {
                'type': 'internal',
                'title': section_title,
                'url': f"/docs/{source_file.replace(' ', '_').lower()}" if source_file else "#",
                'description': description,
                'relevance': result.relevance_score
            }

            references.append(reference)

        return references

# Example usage
if __name__ == "__main__":
    from .retrieval_service import RetrievalResult

    # Initialize service
    citation_service = CitationService()

    # Sample retrieval results
    sample_results = [
        RetrievalResult(
            id="sample_file_introduction_0",
            content="Physical AI represents a paradigm shift in artificial intelligence, focusing on the integration of perception, reasoning, and action in physical environments.",
            source_file="docs/introduction.md",
            score=0.85,
            metadata={
                'chapter': '1',
                'section': 'Introduction',
                'page_number': '5',
                'source_file': 'docs/introduction.md'
            },
            relevance_score=0.82,
            context_similarity=0.78,
            is_relevant=True
        ),
        RetrievalResult(
            id="sample_file_principles_1",
            content="The embodiment principle states that the body plays a crucial role in shaping the mind and intelligent behavior.",
            source_file="docs/principles.md",
            score=0.78,
            metadata={
                'chapter': '2',
                'section': 'Core Principles',
                'page_number': '15',
                'source_file': 'docs/principles.md'
            },
            relevance_score=0.75,
            context_similarity=0.72,
            is_relevant=True
        )
    ]

    # Test citation generation
    citations = citation_service.generate_citations(sample_results)
    print("Generated Citations:")
    for citation in citations:
        print(f"- {citation['formatted_citation']}")
        print(f"  Confidence: {citation['confidence']:.3f}")
        print(f"  URL: {citation['url']}")
        print()

    # Test comprehensive citation creation
    query = "What is Physical AI?"
    response = "Physical AI represents a paradigm shift in artificial intelligence..."
    citation_info = citation_service.create_citation_for_response(query, response, sample_results)

    print("Citation Info:")
    print(f"- Has valid sources: {citation_info['has_valid_sources']}")
    print(f"- Confidence in sources: {citation_info['confidence_in_sources']:.3f}")
    print(f"- Total sources: {citation_info['total_sources_used']}")
    print(f"- Inline citation: {citation_info['inline_citation']}")
    print(f"- Validation: {citation_info['validation']}")