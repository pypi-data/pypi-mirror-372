"""Recursive chunking implementation."""

from typing import List, Optional
from .base import BaseChunker, Chunk


class RecursiveChunker(BaseChunker):
    """Chunks text using recursive splitting with multiple separators."""
    
    def __init__(self, separators: List[str] = None, chunk_size: int = 1000, 
                 overlap: int = 100, **kwargs):
        """
        Initialize recursive chunker.
        
        Args:
            separators: List of separators to try in order
            chunk_size: Target chunk size in characters
            overlap: Number of overlapping characters
        """
        super().__init__(**kwargs)
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        if separators is None:
            self.separators = [
                "\n\n",  # Double newline (paragraphs)
                "\n",    # Single newline
                ". ",    # Sentence endings
                "! ",    # Exclamation marks
                "? ",    # Question marks
                " ",     # Spaces
                ""       # No separator (character-level)
            ]
        else:
            self.separators = separators
    
    def chunk(self, text: str) -> List[Chunk]:
        """Chunk text using recursive splitting."""
        self._validate_input(text)
        
        if len(text) <= self.chunk_size:
            return [Chunk(
                content=text,
                chunk_id=self._get_next_id(),
                metadata={
                    'chunk_type': 'recursive',
                    'chunk_size': len(text),
                    'separators_used': []
                }
            )]
        
        chunks = []
        self._recursive_split(text, chunks, 0)
        return chunks
    
    def _recursive_split(self, text: str, chunks: List[Chunk], 
                        start_index: int, depth: int = 0) -> None:
        """Recursively split text using separators."""
        if len(text) <= self.chunk_size or depth >= len(self.separators):
            # Create chunk if small enough or no more separators
            if text.strip():
                chunk = Chunk(
                    content=text.strip(),
                    chunk_id=self._get_next_id(),
                    start_index=start_index,
                    end_index=start_index + len(text),
                    metadata={
                        'chunk_type': 'recursive',
                        'chunk_size': len(text),
                        'split_depth': depth,
                        'separators_used': self.separators[:depth]
                    }
                )
                chunks.append(chunk)
            return
        
        # Try to split with current separator
        separator = self.separators[depth]
        if separator:
            parts = text.split(separator)
        else:
            # Character-level splitting
            parts = [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]
        
        if len(parts) > 1:
            # Successfully split, process each part
            current_pos = start_index
            for part in parts:
                if part.strip():
                    self._recursive_split(part, chunks, current_pos, depth + 1)
                current_pos += len(part) + len(separator)
        else:
            # Couldn't split with this separator, try next
            self._recursive_split(text, chunks, start_index, depth + 1)
    
    def get_separators(self) -> List[str]:
        """Get the list of separators."""
        return self.separators.copy()
    
    def add_separator(self, separator: str, position: Optional[int] = None) -> None:
        """Add a new separator to the list."""
        if position is None:
            self.separators.append(separator)
        else:
            self.separators.insert(position, separator)
    
    def remove_separator(self, separator: str) -> None:
        """Remove a separator from the list."""
        if separator in self.separators:
            self.separators.remove(separator)



