from typing import List, Dict, Any, Optional, Tuple
import logging
import hashlib
import re
from datetime import datetime
from .vector_store import VectorStoreService
from .embedding_service import EmbeddingService
from .content_processor import ContentProcessor

logger = logging.getLogger(__name__)

class ContentValidationService:
    """Service for validating content quality, consistency, and integrity"""

    def __init__(
        self,
        vector_store: VectorStoreService = None,
        embedding_service: EmbeddingService = None,
        content_processor: ContentProcessor = None
    ):
        self.vector_store = vector_store or VectorStoreService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.content_processor = content_processor or ContentProcessor()

    def validate_content_integrity(self, content: str, source_file: str) -> Dict[str, Any]:
        """Validate the integrity of content"""
        logger.info(f"Validating content integrity for: {source_file}")

        validation_result = {
            'is_valid': True,
            'issues': [],
            'quality_score': 1.0,
            'integrity_checks': {}
        }

        # Check for basic content issues
        integrity_checks = {
            'has_content': len(content.strip()) > 0,
            'no_excessive_whitespace': not self._has_excessive_whitespace(content),
            'no_malformed_markdown': not self._has_malformed_markdown(content),
            'appropriate_length': 50 <= len(content) <= 10000,  # Between 50 and 10,000 characters
            'no_sensitive_content': not self._contains_sensitive_content(content),
            'proper_encoding': self._check_encoding(content)
        }

        validation_result['integrity_checks'] = integrity_checks

        # Calculate quality score based on checks
        passed_checks = sum(1 for check in integrity_checks.values() if check)
        total_checks = len(integrity_checks)
        validation_result['quality_score'] = passed_checks / total_checks if total_checks > 0 else 0.0

        # Identify issues
        for check_name, check_result in integrity_checks.items():
            if not check_result:
                validation_result['is_valid'] = False
                validation_result['issues'].append(self._get_integrity_issue_description(check_name))

        return validation_result

    def _has_excessive_whitespace(self, content: str) -> bool:
        """Check if content has excessive whitespace"""
        # Check for more than 3 consecutive newlines
        if re.search(r'\n\s*\n\s*\n\s*\n', content):
            return True

        # Check for very long lines with only whitespace
        for line in content.split('\n'):
            if len(line.strip()) == 0 and len(line) > 100:
                return True

        return False

    def _has_malformed_markdown(self, content: str) -> bool:
        """Check for malformed markdown syntax"""
        # Check for unmatched brackets
        open_brackets = content.count('[') - content.count(']')
        if open_brackets != 0:
            return True

        # Check for unmatched parentheses in links
        open_parens = content.count('(') - content.count(')')
        if open_parens != 0:
            return True

        # Check for unmatched backticks
        backticks = content.count('`')
        if backticks % 2 != 0:  # Odd number of backticks
            return True

        return False

    def _contains_sensitive_content(self, content: str) -> bool:
        """Check for potentially sensitive content"""
        sensitive_patterns = [
            r'\bpassword\b',
            r'\bsecret\b',
            r'\btoken\b',
            r'\bkey\b',
            r'\bapi.*key\b',
            r'\bauth.*token\b',
            r'\bssh.*key\b',
            r'\bprivate.*key\b'
        ]

        content_lower = content.lower()
        for pattern in sensitive_patterns:
            if re.search(pattern, content_lower):
                return True

        return False

    def _check_encoding(self, content: str) -> bool:
        """Check if content has proper encoding"""
        try:
            # Try to encode and decode to check for encoding issues
            content.encode('utf-8').decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
        except UnicodeEncodeError:
            return False

    def _get_integrity_issue_description(self, check_name: str) -> str:
        """Get description for integrity check issue"""
        descriptions = {
            'has_content': 'Content is empty',
            'no_excessive_whitespace': 'Content has excessive whitespace',
            'no_malformed_markdown': 'Content contains malformed markdown',
            'appropriate_length': 'Content length is inappropriate',
            'no_sensitive_content': 'Content may contain sensitive information',
            'proper_encoding': 'Content has encoding issues'
        }
        return descriptions.get(check_name, f'Issue with {check_name}')

    def validate_content_consistency(
        self,
        content_chunks: List[Dict[str, Any]],
        source_file: str
    ) -> Dict[str, Any]:
        """Validate consistency across content chunks"""
        logger.info(f"Validating content consistency for: {source_file}")

        validation_result = {
            'is_consistent': True,
            'inconsistencies': [],
            'consistency_score': 1.0,
            'chunk_analysis': {}
        }

        if not content_chunks:
            validation_result['consistency_score'] = 0.0
            return validation_result

        # Analyze chunk relationships and consistency
        chunk_analysis = {
            'total_chunks': len(content_chunks),
            'avg_chunk_size': sum(len(chunk.get('content', '')) for chunk in content_chunks) / len(content_chunks) if content_chunks else 0,
            'size_variance': self._calculate_size_variance(content_chunks),
            'semantic_coherence': self._calculate_semantic_coherence(content_chunks),
            'metadata_consistency': self._check_metadata_consistency(content_chunks)
        }

        validation_result['chunk_analysis'] = chunk_analysis

        # Identify inconsistencies
        if chunk_analysis['size_variance'] > 0.5:  # High variance
            validation_result['inconsistencies'].append('High variance in chunk sizes detected')

        if chunk_analysis['semantic_coherence'] < 0.3:  # Low coherence
            validation_result['inconsistencies'].append('Low semantic coherence between chunks')

        if not chunk_analysis['metadata_consistency']:
            validation_result['inconsistencies'].append('Metadata inconsistencies detected')

        # Calculate consistency score
        scores = [
            min(chunk_analysis['semantic_coherence'] * 2, 1.0),  # Boost low coherence scores
            1.0 - min(chunk_analysis['size_variance'], 1.0),    # Lower variance = higher score
            1.0 if chunk_analysis['metadata_consistency'] else 0.5
        ]

        validation_result['consistency_score'] = sum(scores) / len(scores) if scores else 0.0
        validation_result['is_consistent'] = validation_result['consistency_score'] > 0.7

        return validation_result

    def _calculate_size_variance(self, content_chunks: List[Dict[str, Any]]) -> float:
        """Calculate variance in chunk sizes"""
        if len(content_chunks) <= 1:
            return 0.0

        sizes = [len(chunk.get('content', '')) for chunk in content_chunks]
        avg_size = sum(sizes) / len(sizes)

        if avg_size == 0:
            return 1.0  # High variance if average size is 0

        variance = sum((size - avg_size) ** 2 for size in sizes) / len(sizes)
        # Normalize variance (return value between 0 and 1)
        return min(variance / (avg_size ** 2), 1.0) if avg_size > 0 else 1.0

    def _calculate_semantic_coherence(self, content_chunks: List[Dict[str, Any]]) -> float:
        """Calculate semantic coherence between chunks"""
        if len(content_chunks) <= 1:
            return 1.0

        try:
            # Calculate embeddings for each chunk
            embeddings = []
            for chunk in content_chunks:
                content = chunk.get('content', '')[:1000]  # Limit for efficiency
                if content:
                    emb = self.embedding_service.generate_embedding(content)
                    embeddings.append(emb)

            if len(embeddings) < 2:
                return 1.0

            # Calculate average similarity between consecutive chunks
            similarities = []
            for i in range(len(embeddings) - 1):
                emb1 = embeddings[i]
                emb2 = embeddings[i + 1]

                import numpy as np
                array1 = np.array(emb1)
                array2 = np.array(emb2)

                # Calculate cosine similarity
                similarity = np.dot(array1, array2) / (np.linalg.norm(array1) * np.linalg.norm(array2))
                similarities.append(float(similarity))

            if similarities:
                avg_similarity = sum(similarities) / len(similarities)
                return avg_similarity
            else:
                return 0.0

        except Exception as e:
            logger.warning(f"Error calculating semantic coherence: {str(e)}")
            return 0.5  # Return neutral score on error

    def _check_metadata_consistency(self, content_chunks: List[Dict[str, Any]]) -> bool:
        """Check for metadata consistency across chunks"""
        if not content_chunks:
            return True

        # Check if all chunks have consistent source file
        source_files = set(chunk.get('source_file', '') for chunk in content_chunks)
        if len(source_files) > 1:
            return False

        # Check for consistent metadata structure
        expected_keys = set(['id', 'content', 'source_file', 'metadata'])
        for chunk in content_chunks:
            chunk_keys = set(chunk.keys())
            if not expected_keys.issubset(chunk_keys):
                return False

        return True

    def validate_content_quality(
        self,
        content: str,
        source_file: str,
        expected_topics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Validate the quality of content"""
        logger.info(f"Validating content quality for: {source_file}")

        validation_result = {
            'is_high_quality': True,
            'quality_issues': [],
            'quality_score': 1.0,
            'quality_metrics': {}
        }

        # Calculate various quality metrics
        quality_metrics = {
            'readability_score': self._calculate_readability_score(content),
            'topic_coverage': self._calculate_topic_coverage(content, expected_topics or []),
            'technical_accuracy_indicators': self._check_technical_accuracy_indicators(content),
            'completeness_score': self._calculate_completeness_score(content),
            'clarity_score': self._calculate_clarity_score(content)
        }

        validation_result['quality_metrics'] = quality_metrics

        # Identify quality issues
        if quality_metrics['readability_score'] < 0.3:
            validation_result['quality_issues'].append('Low readability score')

        if quality_metrics['topic_coverage'] < 0.2:
            validation_result['quality_issues'].append('Poor topic coverage')

        if not quality_metrics['technical_accuracy_indicators']:
            validation_result['quality_issues'].append('Lacks technical accuracy indicators')

        if quality_metrics['completeness_score'] < 0.4:
            validation_result['quality_issues'].append('Content appears incomplete')

        if quality_metrics['clarity_score'] < 0.5:
            validation_result['quality_issues'].append('Content clarity issues detected')

        # Calculate overall quality score
        scores = [
            quality_metrics['readability_score'],
            quality_metrics['topic_coverage'],
            1.0 if quality_metrics['technical_accuracy_indicators'] else 0.3,
            quality_metrics['completeness_score'],
            quality_metrics['clarity_score']
        ]

        avg_score = sum(scores) / len(scores) if scores else 0.0
        validation_result['quality_score'] = avg_score
        validation_result['is_high_quality'] = avg_score > 0.6

        return validation_result

    def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score based on content structure"""
        if not content:
            return 0.0

        # Simple readability metrics
        sentences = len(re.split(r'[.!?]+', content)) - 1  # Subtract 1 for empty last split
        words = len(content.split())
        syllables = sum(self._count_syllables(word) for word in content.split())

        if sentences == 0 or words == 0:
            return 0.5  # Neutral score

        # Calculate average sentence length and syllables per word
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words if words > 0 else 0

        # Simple readability score (lower complexity = higher readability)
        # Normalize to 0-1 scale
        sentence_complexity = min(avg_sentence_length / 20.0, 1.0)  # Aim for ~20 words per sentence
        word_complexity = min(avg_syllables_per_word / 2.0, 1.0)    # Aim for ~2 syllables per word

        # Higher readability = lower complexity
        readability_score = (1.0 - sentence_complexity) * 0.6 + (1.0 - word_complexity) * 0.4

        return max(min(readability_score, 1.0), 0.0)

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_was_vowel = False

        for i, char in enumerate(word):
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel

        # Handle silent 'e' at the end
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1

        return max(syllable_count, 1)

    def _calculate_topic_coverage(self, content: str, expected_topics: List[str]) -> float:
        """Calculate how well content covers expected topics"""
        if not expected_topics:
            return 1.0

        content_lower = content.lower()
        covered_topics = 0

        for topic in expected_topics:
            if topic.lower() in content_lower:
                covered_topics += 1

        return covered_topics / len(expected_topics) if expected_topics else 0.0

    def _check_technical_accuracy_indicators(self, content: str) -> bool:
        """Check for indicators of technical accuracy"""
        accuracy_indicators = [
            r'\bfigure\s+\d+',  # References to figures
            r'\btable\s+\d+',   # References to tables
            r'\balgorithm\s+\d+',  # References to algorithms
            r'\b(equation|formula)\s+\d+',  # References to equations
            r'\bchapter\s+\d+',  # References to chapters
            r'\bsection\s+\d+',  # References to sections
            r'\bappendix\s+\w+',  # References to appendices
            r'\b(see|refer to)\s+(section|chapter|figure|table)',  # Cross-references
            r'\bcode\b',  # Mentions of code
            r'\bsimulation\b',  # Mentions of simulations
            r'\bexperiment\b',  # Mentions of experiments
            r'\bresult\b',  # Mentions of results
        ]

        content_lower = content.lower()
        for indicator in accuracy_indicators:
            if re.search(indicator, content_lower, re.IGNORECASE):
                return True

        # Also check for technical terminology specific to Physical AI & Robotics
        technical_terms = [
            'embodiment', 'kinematics', 'dynamics', 'control', 'perception',
            'manipulation', 'navigation', 'localization', 'mapping', 'planning',
            'ros', 'gazebo', 'simulation', 'sensor', 'actuator', 'feedback'
        ]

        for term in technical_terms:
            if term in content_lower:
                return True

        return False

    def _calculate_completeness_score(self, content: str) -> float:
        """Calculate completeness score based on content structure"""
        if not content:
            return 0.0

        # Check for common completeness indicators
        has_introduction = bool(re.search(r'\b(introduction|overview|what is)\b', content, re.IGNORECASE))
        has_conclusion = bool(re.search(r'\b(conclusion|summary|in summary|to conclude)\b', content, re.IGNORECASE))
        has_examples = bool(re.search(r'\b(example|case study|demonstration)\b', content, re.IGNORECASE))
        has_diagrams = bool(re.search(r'\b(figure|diagram|graph|chart|image)\b', content, re.IGNORECASE))

        completeness_indicators = [
            has_introduction,
            has_conclusion,
            has_examples,
            has_diagrams
        ]

        # Weighted score based on importance
        weights = [0.3, 0.2, 0.3, 0.2]
        completeness_score = sum(int(indicator) * weight for indicator, weight in zip(completeness_indicators, weights))

        # Also consider content length
        length_factor = min(len(content) / 500, 1.0)  # Cap at 1.0 for 500+ characters

        return (completeness_score + length_factor) / 2

    def _calculate_clarity_score(self, content: str) -> float:
        """Calculate clarity score based on content structure and language"""
        if not content:
            return 0.0

        # Check for clear structure indicators
        has_headings = len(re.findall(r'^#+\s.*$', content, re.MULTILINE)) > 0
        has_lists = len(re.findall(r'^\s*[\*\-\d]\s+.*$', content, re.MULTILINE)) > 0
        has_bold_text = len(re.findall(r'\*\*.*\*\*', content)) > 0 or len(re.findall(r'__.*__', content)) > 0
        has_italics = len(re.findall(r'\*.*\*', content)) > 0 or len(re.findall(r'_.+_', content)) > 0

        structure_indicators = [has_headings, has_lists, has_bold_text, has_italics]
        structure_score = sum(structure_indicators) / len(structure_indicators) if structure_indicators else 0.0

        # Check for clear language patterns
        clear_language_patterns = [
            r'\b(in other words|to put it simply|basically|essentially)\b',
            r'\b(for example|such as|like\b)',
            r'\b(therefore|thus|consequently|as a result)\b',
            r'\b(first|second|third|finally|lastly)\b'
        ]

        clear_language_count = 0
        for pattern in clear_language_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                clear_language_count += 1

        language_score = min(clear_language_count / 3, 1.0)  # Max 3 indicators

        return (structure_score + language_score) / 2

    def validate_content_pipeline(
        self,
        content: str,
        source_file: str,
        content_chunks: List[Dict[str, Any]] = None,
        expected_topics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run complete content validation pipeline"""
        logger.info(f"Running content validation pipeline for: {source_file}")

        # Run all validation checks
        integrity_result = self.validate_content_integrity(content, source_file)
        consistency_result = self.validate_content_consistency(content_chunks or [], source_file)
        quality_result = self.validate_content_quality(content, source_file, expected_topics)

        # Combine all results
        overall_validation = {
            'content_validated': source_file,
            'timestamp': datetime.utcnow().isoformat(),
            'content_hash': hashlib.md5(content.encode()).hexdigest(),
            'integrity_validation': integrity_result,
            'consistency_validation': consistency_result,
            'quality_validation': quality_result,
            'overall_validity': False,
            'overall_score': 0.0,
            'validation_summary': {}
        }

        # Calculate overall validity and score
        integrity_score = integrity_result['quality_score']
        consistency_score = consistency_result['consistency_score']
        quality_score = quality_result['quality_score']

        overall_score = (integrity_score + consistency_score + quality_score) / 3
        overall_validation['overall_score'] = overall_score
        overall_validation['overall_validity'] = overall_score > 0.7

        # Create validation summary
        issues = []
        issues.extend(integrity_result.get('issues', []))
        issues.extend(consistency_result.get('inconsistencies', []))
        issues.extend(quality_result.get('quality_issues', []))

        overall_validation['validation_summary'] = {
            'total_issues': len(issues),
            'critical_issues': [issue for issue in issues if 'sensitive' in issue.lower() or 'malformed' in issue.lower()],
            'warning_issues': [issue for issue in issues if issue not in overall_validation['validation_summary'].get('critical_issues', [])],
            'integrity_score': integrity_score,
            'consistency_score': consistency_score,
            'quality_score': quality_score,
            'overall_score': overall_score,
            'is_valid': overall_validation['overall_validity']
        }

        logger.info(f"Content validation complete: {source_file}, overall score: {overall_score:.3f}")
        return overall_validation

    def validate_content_update(
        self,
        old_content: str,
        new_content: str,
        source_file: str
    ) -> Dict[str, Any]:
        """Validate a content update to ensure quality is maintained"""
        logger.info(f"Validating content update for: {source_file}")

        # Validate the new content
        new_validation = self.validate_content_pipeline(new_content, source_file)

        # Compare with old content if available
        if old_content:
            old_validation = self.validate_content_pipeline(old_content, source_file)

            # Calculate improvement/deterioration
            old_score = old_validation['overall_score']
            new_score = new_validation['overall_score']

            score_change = new_score - old_score
            is_improved = score_change > 0.05  # Improved if score increased by more than 5%
            is_degraded = score_change < -0.05  # Degraded if score decreased by more than 5%

            new_validation['update_analysis'] = {
                'old_overall_score': old_score,
                'new_overall_score': new_score,
                'score_change': score_change,
                'is_improved': is_improved,
                'is_degraded': is_degraded,
                'change_magnitude': abs(score_change)
            }

        return new_validation

# Example usage
if __name__ == "__main__":
    # Initialize service
    validation_service = ContentValidationService()

    # Sample content for validation
    sample_content = """
# Introduction to Physical AI

Physical AI represents a paradigm shift in artificial intelligence, focusing on the integration of perception, reasoning, and action in physical environments. Unlike traditional AI that operates primarily in digital spaces, Physical AI systems must understand and interact with the physical world through sensors and actuators.

## Core Principles

The embodiment principle states that the body plays a crucial role in shaping the mind and intelligent behavior. In Physical AI, this means that the physical form and sensory-motor capabilities of a system directly influence its cognitive processes.

### Morphological Computation

This principle recognizes that the physical structure of a system can perform computations that would otherwise require complex algorithms. For example, the passive dynamics of a walking robot's legs can contribute to energy-efficient locomotion.

## Technical Implementation

The implementation of Physical AI systems typically involves:

1. Sensor integration for environmental perception
2. Real-time processing capabilities
3. Actuator control systems
4. Feedback mechanisms for adaptation

For example, a humanoid robot would incorporate multiple sensors including cameras, IMUs, and force sensors to perceive its environment and maintain balance.
"""

    # Sample chunks for consistency validation
    sample_chunks = [
        {
            'id': 'sample_file_0',
            'content': 'Physical AI represents a paradigm shift in artificial intelligence, focusing on the integration of perception, reasoning, and action in physical environments.',
            'source_file': 'docs/introduction.md',
            'metadata': {'section': 'Introduction', 'chapter': '1'}
        },
        {
            'id': 'sample_file_1',
            'content': 'The embodiment principle states that the body plays a crucial role in shaping the mind and intelligent behavior.',
            'source_file': 'docs/introduction.md',
            'metadata': {'section': 'Core Principles', 'chapter': '1'}
        }
    ]

    # Test content validation
    validation_result = validation_service.validate_content_pipeline(
        sample_content,
        "docs/introduction.md",
        sample_chunks,
        ["Physical AI", "embodiment", "humanoid robots"]
    )

    print("Content Validation Result:")
    print(f"- Overall Validity: {validation_result['overall_validity']}")
    print(f"- Overall Score: {validation_result['overall_score']:.3f}")
    print(f"- Total Issues: {validation_result['validation_summary']['total_issues']}")
    print(f"- Integrity Score: {validation_result['integrity_validation']['quality_score']:.3f}")
    print(f"- Consistency Score: {validation_result['consistency_validation']['consistency_score']:.3f}")
    print(f"- Quality Score: {validation_result['quality_validation']['quality_score']:.3f}")
    print()

    # Test content update validation
    updated_content = sample_content + "\n\n## Additional Section\nThis is new content for the document."
    update_validation = validation_service.validate_content_update(
        sample_content, updated_content, "docs/introduction.md"
    )

    print("Update Validation Result:")
    if 'update_analysis' in update_validation:
        analysis = update_validation['update_analysis']
        print(f"- Old Score: {analysis['old_overall_score']:.3f}")
        print(f"- New Score: {analysis['new_overall_score']:.3f}")
        print(f"- Score Change: {analysis['score_change']:.3f}")
        print(f"- Is Improved: {analysis['is_improved']}")
        print(f"- Is Degraded: {analysis['is_degraded']}")
    else:
        print("Update analysis not available")