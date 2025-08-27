"""
Jajula Chunking - A comprehensive text chunking library for RAG applications.

This package provides various text chunking strategies optimized for 
Retrieval-Augmented Generation (RAG) applications.
"""

__version__ = "0.1.0"
__author__ = "Jajula"
__email__ = "contact@jajula.com"

from .chunkers import (
    FixedSizeChunker,
    SentenceBasedChunker,
    ParagraphBasedChunker,
    SemanticChunker,
    HierarchicalChunker,
    StructureBasedChunker,
    TokenBasedChunker,
    RecursiveChunker,
    AdaptiveChunker,
)
from .utils import TextProcessor, ChunkValidator
from .exceptions import ChunkingError, InvalidConfigError

__all__ = [
    # Chunkers
    "FixedSizeChunker",
    "SentenceBasedChunker", 
    "ParagraphBasedChunker",
    "SemanticChunker",
    "HierarchicalChunker",
    "StructureBasedChunker",
    "TokenBasedChunker",
    "RecursiveChunker",
    "AdaptiveChunker",
    # Utils
    "TextProcessor",
    "ChunkValidator", 
    # Exceptions
    "ChunkingError",
    "InvalidConfigError",
]

def get_version():
    """Get package version."""
    return __version__


def list_chunkers():
    """List all available chunking strategies."""
    return [
        "FixedSizeChunker - Fixed character/word-based chunking",
        "SentenceBasedChunker - Sentence boundary-based chunking", 
        "ParagraphBasedChunker - Paragraph boundary-based chunking",
        "SemanticChunker - AI-powered semantic chunking",
        "HierarchicalChunker - Multi-level hierarchical chunking",
        "StructureBasedChunker - Document structure-based chunking",
        "TokenBasedChunker - Token-count based chunking",
        "RecursiveChunker - Recursive text splitting",
        "AdaptiveChunker - Adaptive chunking based on content",
    ]
