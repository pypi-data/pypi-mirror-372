"""Paragraph-based chunking implementation."""

import re
from typing import List
from .base import BaseChunker, Chunk


class ParagraphBasedChunker(BaseChunker):
    """Chunks text based on paragraph boundaries."""
    
    def __init__(self, max_paragraphs: int = 3, overlap_paragraphs: int = 1, 
                 paragraph_separators: List[str] = None, **kwargs):
        """
        Initialize paragraph-based chunker.
        
        Args:
            max_paragraphs: Maximum paragraphs per chunk
            overlap_paragraphs: Number of overlapping paragraphs
            paragraph_separators: List of paragraph separator patterns
        """
        super().__init__(**kwargs)
        self.max_paragraphs = max_paragraphs
        self.overlap_paragraphs = overlap_paragraphs
        
        if paragraph_separators is None:
            self.paragraph_separators = [r'\n\s*\n', r'\r\n\s*\r\n', r'\n{2,}']
        else:
            self.paragraph_separators = paragraph_separators
    
    def chunk(self, text: str) -> List[Chunk]:
        """Chunk text based on paragraphs."""
        self._validate_input(text)
        
        # Split text into paragraphs
        paragraphs = self._split_into_paragraphs(text)
        
        if not paragraphs:
            return []
        
        chunks = []
        start_idx = 0
        
        while start_idx < len(paragraphs):
            end_idx = min(start_idx + self.max_paragraphs, len(paragraphs))
            chunk_paragraphs = paragraphs[start_idx:end_idx]
            chunk_content = '\n\n'.join(chunk_paragraphs)
            
            if chunk_content.strip():
                chunk = Chunk(
                    content=chunk_content,
                    chunk_id=self._get_next_id(),
                    metadata={
                        'chunk_type': 'paragraph_based',
                        'paragraph_count': len(chunk_paragraphs),
                        'start_paragraph': start_idx,
                        'end_paragraph': end_idx - 1
                    }
                )
                chunks.append(chunk)
            
            # Move start index (accounting for overlap)
            start_idx = max(end_idx - self.overlap_paragraphs, start_idx + 1)
            
        return chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs using separator patterns."""
        # Use the first separator pattern to split
        separator = self.paragraph_separators[0]
        paragraphs = re.split(separator, text)
        
        # Clean up paragraphs
        cleaned_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if para:
                cleaned_paragraphs.append(para)
        
        return cleaned_paragraphs



