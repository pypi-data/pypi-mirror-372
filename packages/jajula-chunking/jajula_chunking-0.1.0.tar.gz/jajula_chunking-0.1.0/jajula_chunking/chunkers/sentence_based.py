"""Sentence-based chunking implementation."""

import nltk
from nltk.tokenize import sent_tokenize
from typing import List
from .base import BaseChunker, Chunk
from ..exceptions import ChunkingError


class SentenceBasedChunker(BaseChunker):
    """Chunks text based on sentence boundaries."""
    
    def __init__(self, max_sentences: int = 5, overlap_sentences: int = 1, 
                 language: str = 'english', **kwargs):
        """
        Initialize sentence-based chunker.
        
        Args:
            max_sentences: Maximum sentences per chunk
            overlap_sentences: Number of overlapping sentences
            language: Language for sentence tokenization
        """
        super().__init__(**kwargs)
        self.max_sentences = max_sentences
        self.overlap_sentences = overlap_sentences
        self.language = language
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
    
    def chunk(self, text: str) -> List[Chunk]:
        """Chunk text based on sentences."""
        self._validate_input(text)
        
        try:
            sentences = sent_tokenize(text, language=self.language)
        except Exception as e:
            raise ChunkingError(f"Sentence tokenization failed: {e}")
        
        if not sentences:
            return []
        
        chunks = []
        start_idx = 0
        
        while start_idx < len(sentences):
            end_idx = min(start_idx + self.max_sentences, len(sentences))
            chunk_sentences = sentences[start_idx:end_idx]
            chunk_content = ' '.join(chunk_sentences)
            
            if chunk_content.strip():
                chunk = Chunk(
                    content=chunk_content,
                    chunk_id=self._get_next_id(),
                    metadata={
                        'chunk_type': 'sentence_based',
                        'sentence_count': len(chunk_sentences),
                        'start_sentence': start_idx,
                        'end_sentence': end_idx - 1
                    }
                )
                chunks.append(chunk)
            
            # Move start index (accounting for overlap)
            start_idx = max(end_idx - self.overlap_sentences, start_idx + 1)
            
        return chunks
