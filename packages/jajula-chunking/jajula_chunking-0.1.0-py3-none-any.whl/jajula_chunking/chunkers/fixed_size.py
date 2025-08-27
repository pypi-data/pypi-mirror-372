"""Fixed-size chunking implementation."""

from typing import List
from .base import BaseChunker, Chunk


class FixedSizeChunker(BaseChunker):
    """Chunks text into fixed-size segments."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 100, 
                 split_on_word: bool = True, **kwargs):
        """
        Initialize fixed-size chunker.
        
        Args:
            chunk_size: Size of each chunk in characters
            overlap: Number of overlapping characters
            split_on_word: Whether to avoid splitting words
        """
        super().__init__(**kwargs)
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.split_on_word = split_on_word
    
    def chunk(self, text: str) -> List[Chunk]:
        """Chunk text into fixed-size segments."""
        self._validate_input(text)
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_content = text[start:end]
            
            # Avoid splitting words if requested
            if self.split_on_word and end < len(text) and not text[end].isspace():
                last_space = chunk_content.rfind(' ')
                if last_space != -1:
                    chunk_content = chunk_content[:last_space]
                    end = start + last_space
            
            if chunk_content.strip():
                chunk = Chunk(
                    content=chunk_content.strip(),
                    chunk_id=self._get_next_id(),
                    start_index=start,
                    end_index=end,
                    metadata={
                        'chunk_type': 'fixed_size',
                        'chunk_size': len(chunk_content),
                        'overlap': self.overlap
                    }
                )
                chunks.append(chunk)
            
            # Move start position (accounting for overlap)
            start = max(end - self.overlap, start + 1)
            
        return chunks
