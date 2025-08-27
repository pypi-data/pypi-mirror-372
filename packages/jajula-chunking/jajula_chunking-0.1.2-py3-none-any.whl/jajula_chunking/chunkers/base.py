"""Base chunker class and interfaces."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    content: str
    chunk_id: str
    start_index: int = 0
    end_index: int = 0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.end_index == 0:
            self.end_index = len(self.content)


class BaseChunker(ABC):
    """Abstract base class for all chunkers."""
    
    def __init__(self, **kwargs):
        """Initialize base chunker with configuration."""
        self.config = kwargs
        self.chunk_counter = 0
    
    @abstractmethod
    def chunk(self, text: str) -> List[Chunk]:
        """
        Chunk the input text.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of Chunk objects
        """
        pass
    
    def _get_next_id(self) -> str:
        """Generate unique chunk ID."""
        self.chunk_counter += 1
        return f"{self.__class__.__name__.lower()}_{self.chunk_counter}"
    
    def _validate_input(self, text: str) -> None:
        """Validate input text."""
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        if not text.strip():
            raise ValueError("Input text cannot be empty")
    
    def reset_counter(self) -> None:
        """Reset chunk counter."""
        self.chunk_counter = 0
        
    def get_config(self) -> Dict[str, Any]:
        """Get chunker configuration."""
        return self.config.copy()

