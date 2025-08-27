"""Custom exceptions for jajula_chunking."""


class ChunkingError(Exception):
    """Base exception for chunking operations."""
    pass


class InvalidConfigError(ChunkingError):
    """Raised when chunker configuration is invalid."""
    pass


class TokenizerError(ChunkingError):
    """Raised when tokenizer operations fail."""
    pass


class SemanticModelError(ChunkingError):
    """Raised when semantic model operations fail."""
    pass


class StructureParsingError(ChunkingError):
    """Raised when document structure parsing fails."""
    pass
