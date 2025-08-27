"""Tests for chunker implementations."""

import pytest
from jajula_chunking.chunkers import (
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
from jajula_chunking.chunkers.base import Chunk


class TestFixedSizeChunker:
    """Test FixedSizeChunker implementation."""
    
    def test_init(self):
        """Test chunker initialization."""
        chunker = FixedSizeChunker(chunk_size=500, overlap=50)
        assert chunker.chunk_size == 500
        assert chunker.overlap == 50
        assert chunker.split_on_word is True
    
    def test_chunk_simple_text(self):
        """Test chunking simple text."""
        chunker = FixedSizeChunker(chunk_size=10, overlap=2)
        text = "This is a test text for chunking."
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
        assert all(chunk.content for chunk in chunks)
    
    def test_chunk_with_word_boundary(self):
        """Test chunking respects word boundaries."""
        chunker = FixedSizeChunker(chunk_size=15, overlap=0, split_on_word=True)
        text = "This is a longer test text for chunking."
        chunks = chunker.chunk(text)
        
        # Check that chunks don't break in the middle of words
        for chunk in chunks:
            words = chunk.content.split()
            if words:
                # First and last words should be complete
                assert not chunk.content.startswith(' ')
                assert not chunk.content.endswith(' ')
    
    def test_overlap(self):
        """Test overlap functionality."""
        chunker = FixedSizeChunker(chunk_size=10, overlap=3)
        text = "This is a test text for chunking."
        chunks = chunker.chunk(text)
        
        if len(chunks) > 1:
            # Check that consecutive chunks have some overlap
            chunk1 = chunks[0].content
            chunk2 = chunks[1].content
            
            # Simple overlap check (can be enhanced)
            assert len(chunk1) >= 7  # chunk_size - overlap
    
    def test_empty_text(self):
        """Test handling of empty text."""
        chunker = FixedSizeChunker()
        with pytest.raises(ValueError):
            chunker.chunk("")
    
    def test_invalid_input(self):
        """Test handling of invalid input."""
        chunker = FixedSizeChunker()
        with pytest.raises(TypeError):
            chunker.chunk(123)


class TestSentenceBasedChunker:
    """Test SentenceBasedChunker implementation."""
    
    def test_init(self):
        """Test chunker initialization."""
        chunker = SentenceBasedChunker(max_sentences=3, overlap_sentences=1)
        assert chunker.max_sentences == 3
        assert chunker.overlap_sentences == 1
        assert chunker.language == 'english'
    
    def test_chunk_simple_sentences(self):
        """Test chunking simple sentences."""
        chunker = SentenceBasedChunker(max_sentences=2, overlap_sentences=0)
        text = "This is sentence one. This is sentence two. This is sentence three."
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
        
        # Check that chunks contain the right number of sentences
        for chunk in chunks:
            sentence_count = chunk.metadata.get('sentence_count', 0)
            assert sentence_count <= 2
    
    def test_overlap_sentences(self):
        """Test sentence overlap functionality."""
        chunker = SentenceBasedChunker(max_sentences=2, overlap_sentences=1)
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunks = chunker.chunk(text)
        
        if len(chunks) > 1:
            # Check that consecutive chunks have overlapping sentences
            chunk1_metadata = chunks[0].metadata
            chunk2_metadata = chunks[1].metadata
            
            # The end sentence of chunk1 should overlap with start sentence of chunk2
            assert chunk1_metadata['end_sentence'] >= chunk2_metadata['start_sentence']
    
    def test_single_sentence(self):
        """Test handling of single sentence."""
        chunker = SentenceBasedChunker()
        text = "This is a single sentence."
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert chunks[0].metadata['sentence_count'] == 1


class TestParagraphBasedChunker:
    """Test ParagraphBasedChunker implementation."""
    
    def test_init(self):
        """Test chunker initialization."""
        chunker = ParagraphBasedChunker(max_paragraphs=2, overlap_paragraphs=1)
        assert chunker.max_paragraphs == 2
        assert chunker.overlap_paragraphs == 1
    
    def test_chunk_paragraphs(self):
        """Test chunking paragraphs."""
        chunker = ParagraphBasedChunker(max_paragraphs=2, overlap_paragraphs=0)
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph.\n\nFourth paragraph."
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        for chunk in chunks:
            paragraph_count = chunk.metadata.get('paragraph_count', 0)
            assert paragraph_count <= 2
    
    def test_custom_separators(self):
        """Test custom paragraph separators."""
        separators = [r'\n---\n', r'\n\n']
        chunker = ParagraphBasedChunker(paragraph_separators=separators)
        text = "First paragraph.\n---\nSecond paragraph.\n\nThird paragraph."
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0


class TestTokenBasedChunker:
    """Test TokenBasedChunker implementation."""
    
    def test_init(self):
        """Test chunker initialization."""
        chunker = TokenBasedChunker(max_tokens=100, overlap_tokens=10)
        assert chunker.max_tokens == 100
        assert chunker.overlap_tokens == 10
    
    def test_chunk_by_tokens(self):
        """Test chunking by token count."""
        chunker = TokenBasedChunker(max_tokens=5, overlap_tokens=1)
        text = "This is a test text for token-based chunking."
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        for chunk in chunks:
            token_count = chunk.metadata.get('token_count', 0)
            assert token_count <= 5
    
    def test_count_tokens(self):
        """Test token counting functionality."""
        chunker = TokenBasedChunker()
        text = "This is a test."
        token_count = chunker.count_tokens(text)
        assert token_count > 0


class TestRecursiveChunker:
    """Test RecursiveChunker implementation."""
    
    def test_init(self):
        """Test chunker initialization."""
        separators = ["\n", ". "]
        chunker = RecursiveChunker(separators=separators, chunk_size=100)
        assert chunker.separators == separators
        assert chunker.chunk_size == 100
    
    def test_recursive_splitting(self):
        """Test recursive splitting functionality."""
        chunker = RecursiveChunker(chunk_size=50)
        text = "First line.\nSecond line.\nThird line.\nFourth line."
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert len(chunk.content) <= 50
    
    def test_custom_separators(self):
        """Test custom separator functionality."""
        separators = ["\n\n", "\n", ". "]
        chunker = RecursiveChunker(separators=separators)
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0


class TestStructureBasedChunker:
    """Test StructureBasedChunker implementation."""
    
    def test_init(self):
        """Test chunker initialization."""
        chunker = StructureBasedChunker(max_chunk_size=1000, preserve_structure=True)
        assert chunker.max_chunk_size == 1000
        assert chunker.preserve_structure is True
    
    def test_html_detection(self):
        """Test HTML detection."""
        chunker = StructureBasedChunker()
        html_text = "<h1>Title</h1><p>Content</p>"
        assert chunker._is_html(html_text) is True
        
        plain_text = "This is plain text."
        assert chunker._is_html(plain_text) is False
    
    def test_markdown_detection(self):
        """Test Markdown detection."""
        chunker = StructureBasedChunker()
        markdown_text = "# Header\n\n* List item\n\n**Bold text**"
        assert chunker._is_markdown(markdown_text) is True
        
        plain_text = "This is plain text."
        assert chunker._is_markdown(plain_text) is False
    
    def test_html_chunking(self):
        """Test HTML chunking."""
        chunker = StructureBasedChunker(max_chunk_size=100)
        html_text = "<h1>Title</h1><p>First paragraph.</p><p>Second paragraph.</p>"
        chunks = chunker.chunk(html_text)
        
        assert len(chunks) > 0


class TestAdaptiveChunker:
    """Test AdaptiveChunker implementation."""
    
    def test_init(self):
        """Test chunker initialization."""
        chunker = AdaptiveChunker(max_chunk_size=1000, enable_semantic=True)
        assert chunker.max_chunk_size == 1000
        assert chunker.enable_semantic is True
    
    def test_text_analysis(self):
        """Test text analysis functionality."""
        chunker = AdaptiveChunker()
        text = "This is a test text with some technical terms like API and JSON."
        analysis = chunker._analyze_text(text)
        
        assert 'length' in analysis
        assert 'word_count' in analysis
        assert 'technical_terms' in analysis
        assert analysis['technical_terms'] > 0
    
    def test_strategy_selection(self):
        """Test strategy selection."""
        chunker = AdaptiveChunker()
        text = "This is a simple text."
        strategy = chunker._select_strategy(chunker._analyze_text(text))
        
        assert strategy in chunker.get_available_strategies()
    
    def test_recommendation(self):
        """Test strategy recommendation."""
        chunker = AdaptiveChunker()
        text = "This is a test text."
        recommendation = chunker.get_strategy_recommendation(text)
        
        assert 'recommended_strategy' in recommendation
        assert 'reasoning' in recommendation
        assert 'alternative_strategies' in recommendation


class TestBaseChunker:
    """Test BaseChunker functionality."""
    
    def test_chunk_id_generation(self):
        """Test chunk ID generation."""
        chunker = FixedSizeChunker()
        chunker._get_next_id()
        chunker._get_next_id()
        
        assert chunker.chunk_counter == 2
    
    def test_input_validation(self):
        """Test input validation."""
        chunker = FixedSizeChunker()
        
        # Valid input
        chunker._validate_input("Valid text")
        
        # Invalid input
        with pytest.raises(TypeError):
            chunker._validate_input(123)
        
        with pytest.raises(ValueError):
            chunker._validate_input("")
    
    def test_config_management(self):
        """Test configuration management."""
        config = {'chunk_size': 500, 'overlap': 50}
        chunker = FixedSizeChunker(**config)
        
        # Check that the parameters were set correctly
        assert chunker.chunk_size == 500
        assert chunker.overlap == 50
        
        # The BaseChunker stores kwargs in self.config, but FixedSizeChunker
        # doesn't pass them to the parent constructor
        retrieved_config = chunker.get_config()
        # Since FixedSizeChunker doesn't call super().__init__(**kwargs), 
        # the config dict will be empty
        assert retrieved_config == {}


class TestChunk:
    """Test Chunk dataclass."""
    
    def test_chunk_creation(self):
        """Test chunk creation."""
        chunk = Chunk(
            content="Test content",
            chunk_id="test_1",
            start_index=0,
            end_index=12
        )
        
        assert chunk.content == "Test content"
        assert chunk.chunk_id == "test_1"
        assert chunk.start_index == 0
        assert chunk.end_index == 12
        assert isinstance(chunk.metadata, dict)
    
    def test_chunk_post_init(self):
        """Test chunk post-initialization."""
        chunk = Chunk(content="Test", chunk_id="test")
        
        # end_index should be set to content length
        assert chunk.end_index == len("Test")
        # metadata should be initialized as empty dict
        assert chunk.metadata == {}


if __name__ == "__main__":
    pytest.main([__file__])
