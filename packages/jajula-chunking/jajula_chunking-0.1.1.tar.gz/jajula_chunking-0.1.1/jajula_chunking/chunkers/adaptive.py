"""Adaptive chunking implementation."""

import re
from typing import List, Dict, Any, Optional, Tuple
from .base import BaseChunker, Chunk
from .fixed_size import FixedSizeChunker
from .sentence_based import SentenceBasedChunker
from .paragraph_based import ParagraphBasedChunker
from .semantic import SemanticChunker


class AdaptiveChunker(BaseChunker):
    """Automatically selects the best chunking strategy based on content analysis."""
    
    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100,
                 enable_semantic: bool = True, **kwargs):
        """
        Initialize adaptive chunker.
        
        Args:
            max_chunk_size: Maximum chunk size in characters
            overlap: Number of overlapping characters
            enable_semantic: Whether to enable semantic chunking
        """
        super().__init__(**kwargs)
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        self.enable_semantic = enable_semantic
        
        # Initialize chunkers
        self.chunkers = {
            'fixed_size': FixedSizeChunker(chunk_size=max_chunk_size, overlap=overlap),
            'sentence_based': SentenceBasedChunker(max_sentences=5, overlap_sentences=1),
            'paragraph_based': ParagraphBasedChunker(max_paragraphs=3, overlap_paragraphs=1)
        }
        
        if enable_semantic:
            try:
                self.chunkers['semantic'] = SemanticChunker(
                    similarity_threshold=0.6,
                    max_chunk_size=max_chunk_size
                )
            except Exception:
                # Fall back to non-semantic if semantic chunker fails
                pass
    
    def chunk(self, text: str) -> List[Chunk]:
        """Chunk text using the best strategy."""
        self._validate_input(text)
        
        # Analyze text characteristics
        analysis = self._analyze_text(text)
        
        # Select best chunking strategy
        strategy = self._select_strategy(analysis)
        
        # Apply selected strategy
        chunker = self.chunkers[strategy]
        chunks = chunker.chunk(text)
        
        # Add strategy information to metadata
        for chunk in chunks:
            chunk.metadata['adaptive_strategy'] = strategy
            chunk.metadata['text_analysis'] = analysis
        
        return chunks
    
    def _analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text characteristics to determine best chunking strategy."""
        analysis = {}
        
        # Text length analysis
        analysis['length'] = len(text)
        analysis['word_count'] = len(text.split())
        
        # Structure analysis
        analysis['has_html'] = bool(re.search(r'<[^>]+>', text))
        analysis['has_markdown'] = self._has_markdown_elements(text)
        analysis['paragraph_count'] = len(re.split(r'\n\s*\n', text))
        analysis['sentence_count'] = len(re.split(r'[.!?]+', text))
        
        # Content complexity analysis
        analysis['avg_sentence_length'] = analysis['word_count'] / max(analysis['sentence_count'], 1)
        analysis['avg_paragraph_length'] = analysis['word_count'] / max(analysis['paragraph_count'], 1)
        
        # Language and domain analysis
        analysis['technical_terms'] = self._count_technical_terms(text)
        analysis['code_blocks'] = self._count_code_blocks(text)
        analysis['urls'] = self._count_urls(text)
        
        # Readability analysis
        analysis['readability_score'] = self._calculate_readability(text)
        
        return analysis
    
    def _has_markdown_elements(self, text: str) -> bool:
        """Check if text contains Markdown elements."""
        markdown_patterns = [
            r'^#+\s',           # Headers
            r'^\*\s',           # Unordered lists
            r'^\d+\.\s',        # Ordered lists
            r'\*\*[^*]+\*\*',   # Bold text
            r'\*[^*]+\*',       # Italic text
            r'\[.*\]\(.*\)',     # Links
            r'`[^`]+`',         # Inline code
            r'```[\s\S]*```',   # Code blocks
        ]
        return any(re.search(pattern, text, re.MULTILINE) for pattern in markdown_patterns)
    
    def _count_technical_terms(self, text: str) -> int:
        """Count technical/specialized terms."""
        # Simple heuristic: count words with specific patterns
        technical_patterns = [
            r'\b[A-Z]{2,}\b',      # Acronyms
            r'\b\w+[A-Z]\w*\b',    # CamelCase
            r'\b\w+_\w+\b',        # Snake_case
            r'\b\d+[A-Za-z]+\b',   # Numbers followed by letters
        ]
        
        count = 0
        for pattern in technical_patterns:
            count += len(re.findall(pattern, text))
        
        return count
    
    def _count_code_blocks(self, text: str) -> int:
        """Count code blocks in text."""
        code_patterns = [
            r'```[\s\S]*?```',     # Markdown code blocks
            r'`[^`]+`',            # Inline code
            r'<code>[\s\S]*?</code>',  # HTML code tags
        ]
        
        count = 0
        for pattern in code_patterns:
            count += len(re.findall(pattern, text))
        
        return count
    
    def _count_urls(self, text: str) -> int:
        """Count URLs in text."""
        url_pattern = r'https?://[^\s]+'
        return len(re.findall(url_pattern, text))
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate a simple readability score."""
        sentences = re.split(r'[.!?]+', text)
        words = text.split()
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simple Flesch-like score (lower = more complex)
        readability = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length)
        return max(0.0, min(100.0, readability))
    
    def _select_strategy(self, analysis: Dict[str, Any]) -> str:
        """Select the best chunking strategy based on text analysis."""
        # Decision tree for strategy selection
        
        # If text is very short, use fixed-size
        if analysis['length'] <= self.max_chunk_size:
            return 'fixed_size'
        
        # If text has HTML/Markdown structure, prefer structure-based
        if analysis['has_html'] or analysis['has_markdown']:
            return 'paragraph_based'  # Fallback to paragraph-based
        
        # If text has many technical terms or code, prefer semantic
        if (analysis['technical_terms'] > 10 or analysis['code_blocks'] > 0) and 'semantic' in self.chunkers:
            return 'semantic'
        
        # If text has good paragraph structure, use paragraph-based
        if analysis['paragraph_count'] > 3 and analysis['avg_paragraph_length'] < 100:
            return 'paragraph_based'
        
        # If text has good sentence structure, use sentence-based
        if analysis['sentence_count'] > 5 and analysis['avg_sentence_length'] < 25:
            return 'sentence_based'
        
        # If text is very long and complex, prefer semantic
        if analysis['length'] > 5000 and analysis['readability_score'] < 50 and 'semantic' in self.chunkers:
            return 'semantic'
        
        # Default to fixed-size for most cases
        return 'fixed_size'
    
    def get_strategy_recommendation(self, text: str) -> Dict[str, Any]:
        """Get detailed strategy recommendation with reasoning."""
        analysis = self._analyze_text(text)
        strategy = self._select_strategy(analysis)
        
        recommendation = {
            'recommended_strategy': strategy,
            'text_analysis': analysis,
            'reasoning': self._explain_strategy_choice(analysis, strategy),
            'alternative_strategies': self._get_alternative_strategies(analysis, strategy)
        }
        
        return recommendation
    
    def _explain_strategy_choice(self, analysis: Dict[str, Any], strategy: str) -> str:
        """Explain why a particular strategy was chosen."""
        reasons = []
        
        if strategy == 'semantic':
            if analysis['technical_terms'] > 10:
                reasons.append("High technical content detected")
            if analysis['code_blocks'] > 0:
                reasons.append("Code blocks present")
            if analysis['readability_score'] < 50:
                reasons.append("Complex text requiring semantic understanding")
        elif strategy == 'paragraph_based':
            if analysis['paragraph_count'] > 3:
                reasons.append("Clear paragraph structure detected")
            if analysis['avg_paragraph_length'] < 100:
                reasons.append("Well-formed paragraphs")
        elif strategy == 'sentence_based':
            if analysis['sentence_count'] > 5:
                reasons.append("Multiple sentences detected")
            if analysis['avg_sentence_length'] < 25:
                reasons.append("Well-formed sentences")
        elif strategy == 'fixed_size':
            reasons.append("Standard approach for general text")
        
        return "; ".join(reasons) if reasons else "Default strategy selected"
    
    def _get_alternative_strategies(self, analysis: Dict[str, Any], primary: str) -> List[str]:
        """Get alternative strategies that could work well."""
        alternatives = []
        
        if primary != 'semantic' and 'semantic' in self.chunkers:
            if analysis['technical_terms'] > 5:
                alternatives.append('semantic')
        
        if primary != 'paragraph_based':
            if analysis['paragraph_count'] > 2:
                alternatives.append('paragraph_based')
        
        if primary != 'sentence_based':
            if analysis['sentence_count'] > 3:
                alternatives.append('sentence_based')
        
        if primary != 'fixed_size':
            alternatives.append('fixed_size')
        
        return alternatives
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available chunking strategies."""
        return list(self.chunkers.keys())
    
    def set_strategy_weights(self, weights: Dict[str, float]) -> None:
        """Set custom weights for strategy selection (for future enhancement)."""
        # This could be used to implement weighted strategy selection
        self.strategy_weights = weights

