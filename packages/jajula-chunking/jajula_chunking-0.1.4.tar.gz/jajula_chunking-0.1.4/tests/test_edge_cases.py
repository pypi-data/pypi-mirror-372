"""
Comprehensive edge case testing for all chunkers.
Tests the specific scenarios that were causing issues.
"""

import pytest
from jajula_chunking.chunkers import (
    FixedSizeChunker,
    SentenceBasedChunker,
    ParagraphBasedChunker,
    TokenBasedChunker,
    RecursiveChunker,
    StructureBasedChunker,
    HierarchicalChunker,
    AdaptiveChunker,
    SemanticChunker,
)
from jajula_chunking.chunkers.base import Chunk


class TestFixedSizeChunkerEdgeCases:
    """Test FixedSizeChunker with edge cases and overlap scenarios."""
    
    def test_short_text_with_large_chunk_size(self):
        """Test short text with chunk size much larger than text."""
        chunker = FixedSizeChunker(chunk_size=1000, overlap=100)
        text = "Hi"
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert chunks[0].content == "Hi"
        assert chunks[0].metadata['is_single_chunk'] is True
        assert chunks[0].metadata['overlap'] == 0
    
    def test_short_text_with_large_overlap(self):
        """Test short text with overlap larger than chunk size."""
        chunker = FixedSizeChunker(chunk_size=22, overlap=50)
        text = "Your long text here..."
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert chunks[0].content == "Your long text here..."
        assert chunks[0].metadata['is_single_chunk'] is True
        assert chunks[0].metadata['overlap'] == 0
    
    def test_chunk_size_equals_text_length(self):
        """Test when chunk size exactly equals text length."""
        chunker = FixedSizeChunker(chunk_size=22, overlap=10)
        text = "Your long text here..."
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert chunks[0].content == "Your long text here..."
        assert chunks[0].metadata['is_single_chunk'] is True
    
    def test_chunk_size_smaller_than_text(self):
        """Test normal case where text needs multiple chunks."""
        chunker = FixedSizeChunker(chunk_size=20, overlap=5)
        text = "This is a much longer text that needs multiple chunks."
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 1
        for chunk in chunks:
            assert chunk.metadata['is_single_chunk'] is False
            assert chunk.metadata['overlap'] == 5
    
    def test_zero_overlap(self):
        """Test with zero overlap."""
        chunker = FixedSizeChunker(chunk_size=30, overlap=0)
        text = "This text will be split into chunks with no overlap."
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 1
        for chunk in chunks:
            assert chunk.metadata['overlap'] == 0
    
    def test_overlap_larger_than_chunk_size(self):
        """Test edge case where overlap > chunk_size."""
        chunker = FixedSizeChunker(chunk_size=15, overlap=20)
        text = "This is a test text for overlap testing."
        chunks = chunker.chunk(text)
        
        # Should still work without infinite loops
        assert len(chunks) > 0
        assert len(chunks) <= len(text)  # Sanity check
    
    def test_empty_text_handling(self):
        """Test handling of empty text."""
        chunker = FixedSizeChunker(chunk_size=100, overlap=20)
        
        with pytest.raises(ValueError):
            chunker.chunk("")
        
        with pytest.raises(ValueError):
            chunker.chunk("   \n\n\t   ")
    
    def test_whitespace_only_text(self):
        """Test text with only whitespace."""
        chunker = FixedSizeChunker(chunk_size=100, overlap=20)
        
        with pytest.raises(ValueError):
            chunker.chunk("   \n\n\t   ")
    
    def test_very_long_words(self):
        """Test text with words longer than chunk size."""
        chunker = FixedSizeChunker(chunk_size=10, overlap=2, split_on_word=True)
        text = "This is a text with verylongwordthatislongerthanthechunksize"
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        # Should handle long words gracefully
    
    def test_unicode_and_special_characters(self):
        """Test text with unicode and special characters."""
        chunker = FixedSizeChunker(chunk_size=20, overlap=5)
        text = "Text with unicode: 你好世界 🌍 🚀 and special chars: @#$%^&*()"
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert len(chunk.content) > 0
    
    def test_boundary_conditions(self):
        """Test boundary conditions for chunk sizes."""
        # Test chunk size = 1
        chunker = FixedSizeChunker(chunk_size=1, overlap=0)
        text = "ABC"
        chunks = chunker.chunk(text)
        assert len(chunks) == 3
        
        # Test chunk size = text length
        chunker = FixedSizeChunker(chunk_size=3, overlap=0)
        chunks = chunker.chunk(text)
        assert len(chunks) == 1
        
        # Test chunk size > text length
        chunker = FixedSizeChunker(chunk_size=5, overlap=0)
        chunks = chunker.chunk(text)
        assert len(chunks) == 1


class TestOverlapScenarios:
    """Test various overlap scenarios across different chunkers."""
    
    def test_sentence_chunker_overlap(self):
        """Test sentence chunker with various overlap settings."""
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        
        # No overlap
        chunker = SentenceBasedChunker(max_sentences=2, overlap_sentences=0)
        chunks = chunker.chunk(text)
        assert len(chunks) == 2
        
        # With overlap
        chunker = SentenceBasedChunker(max_sentences=2, overlap_sentences=1)
        chunks = chunker.chunk(text)
        assert len(chunks) == 4  # With overlap, creates more chunks
    
    def test_paragraph_chunker_overlap(self):
        """Test paragraph chunker with various overlap settings."""
        text = "Para1\n\nPara2\n\nPara3\n\nPara4"
        
        # No overlap
        chunker = ParagraphBasedChunker(max_paragraphs=2, overlap_paragraphs=0)
        chunks = chunker.chunk(text)
        assert len(chunks) == 2
        
        # With overlap
        chunker = ParagraphBasedChunker(max_paragraphs=2, overlap_paragraphs=1)
        chunks = chunker.chunk(text)
        assert len(chunks) == 4  # With overlap, creates more chunks
    
    def test_token_chunker_overlap(self):
        """Test token chunker with various overlap settings."""
        text = "This is a test sentence with multiple words for token testing."
        
        # No overlap
        chunker = TokenBasedChunker(max_tokens=5, overlap_tokens=0)
        chunks = chunker.chunk(text)
        assert len(chunks) > 1
        
        # With overlap
        chunker = TokenBasedChunker(max_tokens=5, overlap_tokens=2)
        chunks = chunker.chunk(text)
        assert len(chunks) > 1


class TestMemoryAndPerformanceEdgeCases:
    """Test memory and performance edge cases."""
    
    def test_very_long_text(self):
        """Test with very long text to ensure no memory issues."""
        # Create a very long text
        long_text = "This is a very long sentence. " * 1000
        
        chunker = FixedSizeChunker(chunk_size=500, overlap=50)
        chunks = chunker.chunk(long_text)
        
        assert len(chunks) > 0
        # Should complete without MemoryError
        
        # Check chunk sizes
        for chunk in chunks:
            assert len(chunk.content) <= 500
    
    def test_many_small_chunks(self):
        """Test creating many small chunks."""
        text = "Word. " * 1000  # 1000 sentences
        
        chunker = SentenceBasedChunker(max_sentences=1, overlap_sentences=0)
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        # Should handle many chunks efficiently
    
    def test_extreme_overlap_ratios(self):
        """Test extreme overlap ratios."""
        text = "This is a test text for extreme overlap testing."
        
        # 90% overlap
        chunker = FixedSizeChunker(chunk_size=20, overlap=18)
        chunks = chunker.chunk(text)
        assert len(chunks) > 0
        
        # 100% overlap (should still work)
        chunker = FixedSizeChunker(chunk_size=20, overlap=20)
        chunks = chunker.chunk(text)
        assert len(chunks) > 0


class TestIntegrationEdgeCases:
    """Test edge cases in integration scenarios."""
    
    def test_multiple_chunkers_pipeline(self):
        """Test pipeline of multiple chunkers with edge cases."""
        text = "Short text."
        
        # First chunk by sentences
        sentence_chunker = SentenceBasedChunker(max_sentences=1, overlap_sentences=0)
        sentence_chunks = sentence_chunker.chunk(text)
        
        # Then chunk each by size
        fixed_chunker = FixedSizeChunker(chunk_size=100, overlap=20)
        all_chunks = []
        
        for sentence_chunk in sentence_chunks:
            sub_chunks = fixed_chunker.chunk(sentence_chunk.content)
            all_chunks.extend(sub_chunks)
        
        assert len(all_chunks) > 0
    
    def test_adaptive_chunker_edge_cases(self):
        """Test adaptive chunker with edge cases."""
        # Very short text
        text = "Hi"
        chunker = AdaptiveChunker(strategies=['fixed_size', 'sentence_based'])
        chunks = chunker.chunk(text)
        assert len(chunks) > 0
        
        # Very long text
        long_text = "This is a sentence. " * 100
        chunks = chunker.chunk(long_text)
        assert len(chunks) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
