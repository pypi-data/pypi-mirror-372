# Jajula Chunking

A comprehensive Python library for text chunking strategies optimized for RAG (Retrieval-Augmented Generation) applications.

## Features

- **9 Different Chunking Strategies** - From simple fixed-size to advanced semantic chunking
- **RAG-Optimized** - Designed specifically for retrieval-augmented generation workflows
- **Easy to Use** - Simple, consistent API across all chunkers
- **Extensible** - Base classes for creating custom chunking strategies
- **Production Ready** - Comprehensive error handling and validation

## Installation

```bash
pip install jajula-chunking
```

## Quick Start

```python
from jajula_chunking import FixedSizeChunker, SemanticChunker

# Fixed-size chunking
chunker = FixedSizeChunker(chunk_size=500, overlap=50)
chunks = chunker.chunk("Your long text here...")

# Semantic chunking
semantic_chunker = SemanticChunker(similarity_threshold=0.6)
semantic_chunks = semantic_chunker.chunk("Your text here...")

for chunk in chunks:
    print(f"ID: {chunk.chunk_id}")
    print(f"Content: {chunk.content}")
    print(f"Metadata: {chunk.metadata}")
    print("---")
```

## Available Chunkers

1. **FixedSizeChunker** - Fixed character/word-based chunking
2. **SentenceBasedChunker** - Sentence boundary-based chunking
3. **ParagraphBasedChunker** - Paragraph boundary-based chunking
4. **SemanticChunker** - AI-powered semantic chunking
5. **HierarchicalChunker** - Multi-level hierarchical chunking
6. **StructureBasedChunker** - Document structure-based chunking (HTML/Markdown)
7. **TokenBasedChunker** - Token-count based chunking
8. **RecursiveChunker** - Recursive text splitting with multiple separators
9. **AdaptiveChunker** - Adaptive chunking based on content analysis

## Documentation

For detailed documentation and examples, visit: [Documentation Link]

## Contributing

Contributions are welcome! Please read our contributing guidelines for details.

## License

MIT License - see LICENSE file for details.

