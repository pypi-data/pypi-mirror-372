"""Comprehensive test suite for Jajula Chunking package."""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from typing import List

from jajula_chunking import (
    FixedSizeChunker, SentenceBasedChunker, ParagraphBasedChunker,
    SemanticChunker, TokenBasedChunker, RecursiveChunker, StructureBasedChunker,
    HierarchicalChunker, AdaptiveChunker, TextProcessor, ChunkValidator
)
from jajula_chunking.chunkers.base import Chunk, BaseChunker
from jajula_chunking.exceptions import (
    ChunkingError, InvalidConfigError, TokenizerError, 
    SemanticModelError, StructureParsingError
)


class TestFixedSizeChunker:
    """Comprehensive tests for FixedSizeChunker."""
    
    def test_basic_functionality(self):
        """Test basic fixed-size chunking."""
        text = "This is a test text that should be chunked into fixed size segments."
        chunker = FixedSizeChunker(chunk_size=20, overlap=5)
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        assert all(len(chunk.content) <= 20 for chunk in chunks)
        assert chunks[0].content == "This is a test text"
    
    def test_overlap_functionality(self):
        """Test that overlap works correctly."""
        text = "This is a test text that should be chunked."
        chunker = FixedSizeChunker(chunk_size=15, overlap=5)
        chunks = chunker.chunk(text)
        
        if len(chunks) > 1:
            # Check that chunks overlap
            first_chunk_end = chunks[0].end_index
            second_chunk_start = chunks[1].start_index
            overlap_size = first_chunk_end - second_chunk_start
            assert overlap_size >= 0
    
    def test_split_on_word_true(self):
        """Test chunking with split_on_word=True."""
        text = "This is a test text that should not split words."
        chunker = FixedSizeChunker(chunk_size=10, overlap=2, split_on_word=True)
        chunks = chunker.chunk(text)
        
        for chunk in chunks:
            # Check that chunks don't end in the middle of words
            if chunk.content and not chunk.content.endswith(' '):
                # Find the last word boundary
                last_space = chunk.content.rfind(' ')
                if last_space != -1:
                    # Content should end at a word boundary
                    assert chunk.content[last_space+1:] in text
    
    def test_split_on_word_false(self):
        """Test chunking with split_on_word=False."""
        text = "This is a test text."
        chunker = FixedSizeChunker(chunk_size=8, overlap=2, split_on_word=False)
        chunks = chunker.chunk(text)
        
        # Should create more chunks when not respecting word boundaries
        assert len(chunks) > 0
    
    def test_empty_text(self):
        """Test chunking empty text."""
        chunker = FixedSizeChunker()
        chunks = chunker.chunk("")
        assert len(chunks) == 0
    
    def test_short_text(self):
        """Test chunking text shorter than chunk_size."""
        text = "Short text"
        chunker = FixedSizeChunker(chunk_size=100)
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert chunks[0].content == text
    
    def test_large_overlap(self):
        """Test chunking with overlap larger than chunk_size."""
        text = "This is a test text for large overlap testing."
        chunker = FixedSizeChunker(chunk_size=10, overlap=15)
        chunks = chunker.chunk(text)
        
        # Should still work without infinite loops
        assert len(chunks) > 0
    
    def test_zero_overlap(self):
        """Test chunking with zero overlap."""
        text = "This is a test text for zero overlap testing."
        chunker = FixedSizeChunker(chunk_size=15, overlap=0)
        chunks = chunker.chunk(text)
        
        # Should create non-overlapping chunks
        for i in range(len(chunks) - 1):
            assert chunks[i].end_index <= chunks[i+1].start_index
    
    def test_whitespace_handling(self):
        """Test handling of whitespace in text."""
        text = "   Text with   extra   spaces   "
        chunker = FixedSizeChunker(chunk_size=20)
        chunks = chunker.chunk(text)
        
        for chunk in chunks:
            # Chunks should be stripped of leading/trailing whitespace
            assert chunk.content == chunk.content.strip()
    
    def test_metadata_correctness(self):
        """Test that metadata is correctly set."""
        text = "Test text"
        chunker = FixedSizeChunker(chunk_size=10, overlap=2)
        chunks = chunker.chunk(text)
        
        for chunk in chunks:
            assert chunk.metadata['chunk_type'] == 'fixed_size'
            assert 'chunk_size' in chunk.metadata
            assert chunk.metadata['overlap'] == 2
    
    def test_chunk_id_uniqueness(self):
        """Test that chunk IDs are unique."""
        text = "This is a longer text that will create multiple chunks for testing."
        chunker = FixedSizeChunker(chunk_size=10, overlap=2)
        chunks = chunker.chunk(text)
        
        chunk_ids = [chunk.chunk_id for chunk in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))
    
    def test_index_correctness(self):
        """Test that start and end indices are correct."""
        text = "Test text for index validation"
        chunker = FixedSizeChunker(chunk_size=10, overlap=2)
        chunks = chunker.chunk(text)
        
        for chunk in chunks:
            assert chunk.start_index >= 0
            assert chunk.end_index <= len(text)
            assert chunk.start_index < chunk.end_index
            assert chunk.content == text[chunk.start_index:chunk.end_index].strip()


class TestSentenceBasedChunker:
    """Comprehensive tests for SentenceBasedChunker."""
    
    def test_basic_sentence_chunking(self):
        """Test basic sentence-based chunking."""
        text = "This is the first sentence. This is the second sentence! And this is the third sentence?"
        chunker = SentenceBasedChunker()
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 3
        assert "first sentence" in chunks[0].content
        assert "second sentence" in chunks[1].content
        assert "third sentence" in chunks[2].content
    
    def test_sentence_with_overlap(self):
        """Test sentence chunking with overlap."""
        text = "First sentence. Second sentence. Third sentence."
        chunker = SentenceBasedChunker(overlap_sentences=1)
        chunks = chunker.chunk(text)
        
        # With overlap, should have more chunks or overlapping content
        assert len(chunks) >= 3
    
    def test_complex_sentence_detection(self):
        """Test detection of complex sentence patterns."""
        text = "Dr. Smith said: 'Hello there!' Mr. Jones replied. What about 3.14? Let's go!"
        chunker = SentenceBasedChunker()
        chunks = chunker.chunk(text)
        
        # Should handle abbreviations and numbers correctly
        assert len(chunks) > 0
    
    def test_empty_sentences(self):
        """Test handling of empty sentences."""
        text = "First sentence. . Second sentence."
        chunker = SentenceBasedChunker()
        chunks = chunker.chunk(text)
        
        # Should filter out empty sentences
        for chunk in chunks:
            assert chunk.content.strip()
    
    def test_single_sentence(self):
        """Test chunking single sentence."""
        text = "This is a single sentence."
        chunker = SentenceBasedChunker()
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert chunks[0].content == text
    
    def test_no_sentence_endings(self):
        """Test text without sentence endings."""
        text = "This text has no sentence endings"
        chunker = SentenceBasedChunker()
        chunks = chunker.chunk(text)
        
        # Should treat entire text as one sentence
        assert len(chunks) == 1
        assert chunks[0].content == text


class TestParagraphBasedChunker:
    """Comprehensive tests for ParagraphBasedChunker."""
    
    def test_basic_paragraph_chunking(self):
        """Test basic paragraph-based chunking."""
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunker = ParagraphBasedChunker()
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 3
        assert "First paragraph" in chunks[0].content
        assert "Second paragraph" in chunks[1].content
        assert "Third paragraph" in chunks[2].content
    
    def test_paragraph_with_overlap(self):
        """Test paragraph chunking with overlap."""
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunker = ParagraphBasedChunker(overlap_paragraphs=1)
        chunks = chunker.chunk(text)
        
        # With overlap, should have overlapping content
        assert len(chunks) >= 3
    
    def test_single_paragraph(self):
        """Test chunking single paragraph."""
        text = "This is a single paragraph without any line breaks."
        chunker = ParagraphBasedChunker()
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 1
        assert chunks[0].content == text
    
    def test_mixed_line_breaks(self):
        """Test handling of mixed line break patterns."""
        text = "First paragraph.\n\n\nSecond paragraph.\n\n\n\nThird paragraph."
        chunker = ParagraphBasedChunker()
        chunks = chunker.chunk(text)
        
        # Should handle multiple consecutive line breaks
        assert len(chunks) == 3
    
    def test_no_paragraph_breaks(self):
        """Test text without paragraph breaks."""
        text = "This text has no paragraph breaks"
        chunker = ParagraphBasedChunker()
        chunks = chunker.chunk(text)
        
        # Should treat entire text as one paragraph
        assert len(chunks) == 1
        assert chunks[0].content == text


class TestSemanticChunker:
    """Comprehensive tests for SemanticChunker."""
    
    @patch('jajula_chunking.chunkers.semantic.SentenceTransformer')
    def test_basic_semantic_chunking(self, mock_transformer):
        """Test basic semantic chunking."""
        # Mock the sentence transformer
        mock_model = MagicMock()
        mock_transformer.return_value = mock_model
        mock_model.encode.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        
        text = "First sentence. Second sentence."
        chunker = SemanticChunker(similarity_threshold=0.8)
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        mock_model.encode.assert_called()
    
    @patch('jajula_chunking.chunkers.semantic.SentenceTransformer')
    def test_similarity_threshold_effect(self, mock_transformer):
        """Test effect of similarity threshold."""
        mock_model = MagicMock()
        mock_transformer.return_value = mock_model
        mock_model.encode.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        
        text = "First sentence. Second sentence."
        
        # Test with high threshold
        chunker_high = SemanticChunker(similarity_threshold=0.9)
        chunks_high = chunker_high.chunk(text)
        
        # Test with low threshold
        chunker_low = SemanticChunker(similarity_threshold=0.1)
        chunks_low = chunker_low.chunk(text)
        
        # Should produce different results
        assert len(chunks_high) != len(chunks_low) or chunks_high != chunks_low
    
    def test_model_loading_error(self):
        """Test handling of model loading errors."""
        with pytest.raises(SemanticModelError):
            SemanticChunker(model_name="invalid_model_name")


class TestTokenBasedChunker:
    """Comprehensive tests for TokenBasedChunker."""
    
    def test_basic_token_chunking(self):
        """Test basic token-based chunking."""
        text = "This is a test text for token-based chunking."
        chunker = TokenBasedChunker(max_tokens=10, overlap_tokens=2)
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert 'token_count' in chunk.metadata
    
    def test_token_count_accuracy(self):
        """Test that token counts are accurate."""
        text = "Hello world"
        chunker = TokenBasedChunker(max_tokens=5)
        chunks = chunker.chunk(text)
        
        for chunk in chunks:
            assert chunk.metadata['token_count'] <= 5
    
    def test_different_models(self):
        """Test different tokenizer models."""
        text = "Test text"
        
        # Test with different models
        chunker_gpt2 = TokenBasedChunker(model_name="gpt2")
        chunks_gpt2 = chunker_gpt2.chunk(text)
        
        chunker_cl100k = TokenBasedChunker(model_name="cl100k_base")
        chunks_cl100k = chunker_cl100k.chunk(text)
        
        # Should work with different models
        assert len(chunks_gpt2) > 0
        assert len(chunks_cl100k) > 0
    
    def test_invalid_model(self):
        """Test handling of invalid model names."""
        with pytest.raises(TokenizerError):
            TokenBasedChunker(model_name="invalid_model")


class TestRecursiveChunker:
    """Comprehensive tests for RecursiveChunker."""
    
    def test_basic_recursive_chunking(self):
        """Test basic recursive chunking."""
        text = "First part. Second part. Third part."
        chunker = RecursiveChunker(separators=['.', '!', '?'])
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
    
    def test_custom_separators(self):
        """Test chunking with custom separators."""
        text = "Part1|Part2|Part3"
        chunker = RecursiveChunker(separators=['|'])
        chunks = chunker.chunk(text)
        
        assert len(chunks) == 3
        assert "Part1" in chunks[0].content
        assert "Part2" in chunks[1].content
        assert "Part3" in chunks[2].content
    
    def test_recursive_splitting(self):
        """Test recursive splitting behavior."""
        text = "Level1.Level2.Level3"
        chunker = RecursiveChunker(separators=['.', 'Level'])
        chunks = chunker.chunk(text)
        
        # Should split recursively
        assert len(chunks) > 1
    
    def test_empty_separators(self):
        """Test handling of empty separators list."""
        text = "Test text"
        chunker = RecursiveChunker(separators=[])
        chunks = chunker.chunk(text)
        
        # Should treat entire text as one chunk
        assert len(chunks) == 1
        assert chunks[0].content == text


class TestStructureBasedChunker:
    """Comprehensive tests for StructureBasedChunker."""
    
    def test_html_chunking(self):
        """Test HTML structure-based chunking."""
        html_text = "<html><body><h1>Title</h1><p>Paragraph 1</p><p>Paragraph 2</p></body></html>"
        chunker = StructureBasedChunker()
        chunks = chunker.chunk(html_text)
        
        assert len(chunks) > 0
        # Should extract content from HTML tags
        assert any("Title" in chunk.content for chunk in chunks)
    
    def test_markdown_chunking(self):
        """Test Markdown structure-based chunking."""
        markdown_text = "# Title\n\n## Subtitle\n\nThis is a paragraph.\n\n- List item 1\n- List item 2"
        chunker = StructureBasedChunker()
        chunks = chunker.chunk(markdown_text)
        
        assert len(chunks) > 0
        # Should extract content from Markdown structure
        assert any("Title" in chunk.content for chunk in chunks)
    
    def test_plain_text_fallback(self):
        """Test fallback to plain text when no structure detected."""
        text = "This is plain text without any structure."
        chunker = StructureBasedChunker()
        chunks = chunker.chunk(text)
        
        # Should still create chunks
        assert len(chunks) > 0
    
    def test_mixed_content(self):
        """Test chunking mixed HTML and text content."""
        mixed_text = "<h1>Title</h1>Plain text here.<p>More HTML</p>"
        chunker = StructureBasedChunker()
        chunks = chunker.chunk(mixed_text)
        
        assert len(chunks) > 0


class TestHierarchicalChunker:
    """Comprehensive tests for HierarchicalChunker."""
    
    def test_basic_hierarchical_chunking(self):
        """Test basic hierarchical chunking."""
        text = "Level 1 content. Level 2 content. Level 3 content."
        chunker = HierarchicalChunker(levels=3)
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        # Should create hierarchical structure
        for chunk in chunks:
            assert hasattr(chunk, 'level')
            assert chunk.level >= 1
    
    def test_multiple_levels(self):
        """Test chunking with multiple levels."""
        text = "Document with multiple levels of content structure."
        chunker = HierarchicalChunker(levels=2)
        chunks = chunker.chunk(text)
        
        # Should create chunks at different levels
        levels = set(chunk.level for chunk in chunks)
        assert len(levels) > 1
    
    def test_level_granularity(self):
        """Test different level granularity settings."""
        text = "Test text for granularity testing."
        
        chunker_fine = HierarchicalChunker(levels=5, granularity='fine')
        chunks_fine = chunker_fine.chunk(text)
        
        chunker_coarse = HierarchicalChunker(levels=3, granularity='coarse')
        chunks_coarse = chunker_coarse.chunk(text)
        
        # Should produce different results
        assert len(chunks_fine) != len(chunks_coarse) or chunks_fine != chunks_coarse


class TestAdaptiveChunker:
    """Comprehensive tests for AdaptiveChunker."""
    
    def test_basic_adaptive_chunking(self):
        """Test basic adaptive chunking."""
        text = "This is a test text for adaptive chunking."
        chunker = AdaptiveChunker()
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        # Should automatically select appropriate strategy
        assert hasattr(chunks[0], 'metadata')
    
    def test_strategy_selection(self):
        """Test automatic strategy selection."""
        # Test with structured text
        structured_text = "<h1>Title</h1><p>Content</p>"
        chunker = AdaptiveChunker()
        chunks_structured = chunker.chunk(structured_text)
        
        # Test with plain text
        plain_text = "Plain text content."
        chunks_plain = chunker.chunk(plain_text)
        
        # Should select different strategies
        assert len(chunks_structured) > 0
        assert len(chunks_plain) > 0
    
    def test_custom_strategies(self):
        """Test with custom strategy configurations."""
        text = "Test text"
        strategies = {
            'fixed_size': {'chunk_size': 10, 'overlap': 2},
            'sentence_based': {'overlap_sentences': 1}
        }
        chunker = AdaptiveChunker(strategies=strategies)
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0


class TestTextProcessor:
    """Comprehensive tests for TextProcessor."""
    
    def test_clean_text_basic(self):
        """Test basic text cleaning."""
        text = "  This   is   a   test   text.  "
        cleaned = TextProcessor.clean_text(text)
        
        assert cleaned == "This is a test text."
        assert "   " not in cleaned
    
    def test_clean_text_remove_html(self):
        """Test HTML removal in text cleaning."""
        text = "<h1>Title</h1><p>Content</p>"
        cleaned = TextProcessor.clean_text(text, remove_html=True)
        
        assert "<h1>" not in cleaned
        assert "<p>" not in cleaned
        assert "Title" in cleaned
        assert "Content" in cleaned
    
    def test_clean_text_normalize_whitespace(self):
        """Test whitespace normalization."""
        text = "Line 1\n\n\nLine 2\n\n\n\nLine 3"
        cleaned = TextProcessor.clean_text(text, normalize_whitespace=True)
        
        assert "\n\n\n" not in cleaned
        assert "\n\n" in cleaned or "Line 1 Line 2 Line 3" in cleaned
    
    def test_clean_text_remove_special_chars(self):
        """Test special character removal."""
        text = "Hello @#$%^&*() World!"
        cleaned = TextProcessor.clean_text(text, remove_special_chars=True)
        
        assert "@#$%^&*()" not in cleaned
        assert "Hello () World!" in cleaned
    
    def test_remove_html_tags(self):
        """Test HTML tag removal."""
        text = "<div><span>Hello</span> <strong>World</strong></div>"
        cleaned = TextProcessor.remove_html_tags(text)
        
        assert "<div>" not in cleaned
        assert "<span>" not in cleaned
        assert "<strong>" not in cleaned
        assert "Hello World" in cleaned
    
    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        text = "  Multiple    spaces   and\n\n\nline\n\n\nbreaks  "
        normalized = TextProcessor.normalize_whitespace(text)
        
        assert "   " not in normalized
        assert "\n\n\n" not in normalized
        assert normalized.startswith("Multiple")
        assert normalized.endswith("breaks")
    
    def test_remove_special_characters(self):
        """Test special character removal."""
        text = "Hello @#$%^&*() World! 123"
        
        # Keep punctuation
        cleaned_punct = TextProcessor.remove_special_characters(text, keep_punctuation=True)
        assert "Hello () World! 123" in cleaned_punct
        assert "@#$%^&*" not in cleaned_punct
        
        # Remove punctuation
        cleaned_no_punct = TextProcessor.remove_special_characters(text, keep_punctuation=False)
        assert "Hello  World 123" in cleaned_no_punct
        assert "!" not in cleaned_no_punct
    
    def test_extract_sentences(self):
        """Test sentence extraction."""
        text = "First sentence. Second sentence! Third sentence?"
        sentences = TextProcessor.extract_sentences(text)
        
        assert len(sentences) == 3
        assert "First sentence" in sentences[0]
        assert "Second sentence" in sentences[1]
        assert "Third sentence" in sentences[2]
    
    def test_extract_paragraphs(self):
        """Test paragraph extraction."""
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        paragraphs = TextProcessor.extract_paragraphs(text)
        
        assert len(paragraphs) == 3
        assert "First paragraph" in paragraphs[0]
        assert "Second paragraph" in paragraphs[1]
        assert "Third paragraph" in paragraphs[2]
    
    def test_extract_words(self):
        """Test word extraction."""
        text = "Hello world! This is a test."
        words = TextProcessor.extract_words(text, min_length=3)
        
        assert "hello" in words
        assert "world" in words
        assert "this" in words
        assert "is" not in words  # Too short
        assert "a" not in words   # Too short
    
    def test_count_words(self):
        """Test word counting."""
        text = "Hello world! This is a test."
        count = TextProcessor.count_words(text)
        
        assert count == 6
    
    def test_count_characters(self):
        """Test character counting."""
        text = "Hello world"
        
        with_spaces = TextProcessor.count_characters(text, include_spaces=True)
        without_spaces = TextProcessor.count_characters(text, include_spaces=False)
        
        assert with_spaces == 11
        assert without_spaces == 10
    
    def test_get_text_statistics(self):
        """Test text statistics calculation."""
        text = "First sentence. Second sentence!\n\nNew paragraph."
        stats = TextProcessor.get_text_statistics(text)
        
        assert stats['characters'] > 0
        assert stats['words'] > 0
        assert stats['sentences'] == 3
    
    def test_detect_language(self):
        """Test language detection."""
        english_text = "The quick brown fox jumps over the lazy dog."
        detected = TextProcessor.detect_language(english_text)
        assert detected in ['english', 'spanish', 'french', 'german', 'unknown']
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "The quick brown fox jumps over the lazy dog. The fox is quick and brown."
        keywords = TextProcessor.extract_keywords(text, max_keywords=5, min_length=3)
        
        assert len(keywords) <= 5
        assert "quick" in keywords
        assert "brown" in keywords
        assert "fox" in keywords
        assert "the" not in keywords  # Stop word
    
    def test_split_text_into_chunks(self):
        """Test text splitting into chunks."""
        text = "This is a longer text that should be split into multiple chunks."
        chunks = TextProcessor.split_text_into_chunks(text, chunk_size=20, overlap=5)
        
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 20
            assert chunk.strip()


class TestChunkValidator:
    """Comprehensive tests for ChunkValidator."""
    
    def test_validate_chunk_valid(self):
        """Test validation of valid chunk."""
        chunk = Chunk(
            content="This is a valid chunk with sufficient content.",
            chunk_id="test_1",
            start_index=0,
            end_index=50
        )
        
        result = ChunkValidator.validate_chunk(chunk, min_length=10, max_length=1000)
        
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        assert result['score'] > 80
    
    def test_validate_chunk_empty_content(self):
        """Test validation of chunk with empty content."""
        chunk = Chunk(
            content="",
            chunk_id="test_1"
        )
        
        result = ChunkValidator.validate_chunk(chunk)
        
        assert result['is_valid'] is False
        assert "empty" in result['errors'][0]
        assert result['score'] < 50
    
    def test_validate_chunk_too_short(self):
        """Test validation of chunk that's too short."""
        chunk = Chunk(
            content="Short",
            chunk_id="test_1"
        )
        
        result = ChunkValidator.validate_chunk(chunk, min_length=10)
        
        assert result['is_valid'] is False
        assert "too short" in result['errors'][0]
    
    def test_validate_chunk_too_long(self):
        """Test validation of chunk that's too long."""
        chunk = Chunk(
            content="A" * 2000,  # Very long content
            chunk_id="test_1"
        )
        
        result = ChunkValidator.validate_chunk(chunk, max_length=1000)
        
        assert result['is_valid'] is False
        assert "too long" in result['errors'][0]
    
    def test_validate_chunk_missing_id(self):
        """Test validation of chunk without ID."""
        chunk = Chunk(
            content="Valid content",
            chunk_id=""
        )
        
        result = ChunkValidator.validate_chunk(chunk)
        
        assert result['is_valid'] is False
        assert "ID is missing" in result['errors'][0]
    
    def test_validate_chunk_invalid_metadata(self):
        """Test validation of chunk with invalid metadata."""
        chunk = Chunk(
            content="Valid content",
            chunk_id="test_1"
        )
        chunk.metadata = "invalid"  # Should be dict
        
        result = ChunkValidator.validate_chunk(chunk)
        
        assert result['is_valid'] is False
        assert "metadata must be a dictionary" in result['errors'][0]
    
    def test_validate_chunk_invalid_indices(self):
        """Test validation of chunk with invalid indices."""
        chunk = Chunk(
            content="Valid content",
            chunk_id="test_1",
            start_index=10,
            end_index=5  # End before start
        )
        
        result = ChunkValidator.validate_chunk(chunk)
        
        assert result['is_valid'] is False
        assert "End index is before start index" in result['errors'][0]
    
    def test_validate_chunks_list(self):
        """Test validation of chunk list."""
        chunks = [
            Chunk(content="First chunk", chunk_id="chunk_1"),
            Chunk(content="Second chunk", chunk_id="chunk_2"),
            Chunk(content="Third chunk", chunk_id="chunk_3")
        ]
        
        result = ChunkValidator.validate_chunks(chunks)
        
        assert result['is_valid'] is True
        assert result['overall_score'] > 80
        assert len(result['chunk_results']) == 3
        assert result['summary']['total_chunks'] == 3
        assert result['summary']['valid_chunks'] == 3
    
    def test_validate_chunks_duplicate_ids(self):
        """Test validation of chunks with duplicate IDs."""
        chunks = [
            Chunk(content="First chunk", chunk_id="chunk_1"),
            Chunk(content="Second chunk", chunk_id="chunk_1"),  # Duplicate ID
            Chunk(content="Third chunk", chunk_id="chunk_3")
        ]
        
        result = ChunkValidator.validate_chunks(chunks)
        
        assert result['is_valid'] is False
        assert "Duplicate chunk IDs found" in result['errors'][0]
    
    def test_validate_chunks_invalid_input(self):
        """Test validation with invalid input."""
        result = ChunkValidator.validate_chunks("not a list")
        
        assert result['is_valid'] is False
        assert "Input must be a list of chunks" in result['errors'][0]
    
    def test_validate_chunks_empty_list(self):
        """Test validation of empty chunk list."""
        result = ChunkValidator.validate_chunks([])
        
        assert result['is_valid'] is False
        assert "No chunks provided" in result['errors'][0]
    
    def test_content_quality_check(self):
        """Test content quality checking."""
        # Test excessive whitespace
        content = "Text   with   excessive   spaces"
        quality = ChunkValidator._check_content_quality(content)
        
        assert "Excessive whitespace detected" in quality['warnings']
        
        # Test repeated characters
        content = "Text with repeated characters!!!!!"
        quality = ChunkValidator._check_content_quality(content)
        
        assert "Repeated characters detected" in quality['warnings']
        
        # Test very long words
        content = "Text with verylongwordthatiswaytoolong"
        quality = ChunkValidator._check_content_quality(content)
        
        assert any("Very long words detected" in warning for warning in quality['warnings'])
    
    def test_analyze_chunk_overlap(self):
        """Test chunk overlap analysis."""
        chunks = [
            Chunk(content="First chunk content", chunk_id="chunk_1"),
            Chunk(content="Second chunk content", chunk_id="chunk_2"),
            Chunk(content="Third chunk content", chunk_id="chunk_3")
        ]
        
        analysis = ChunkValidator._analyze_chunk_overlap(chunks)
        
        assert 'overlap_detected' in analysis['analysis']
        assert 'chunk_lengths' in analysis['analysis']
        assert 'avg_length' in analysis['analysis']
        assert 'size_consistency' in analysis['analysis']
    
    def test_get_chunk_statistics(self):
        """Test chunk statistics calculation."""
        chunks = [
            Chunk(content="First chunk", chunk_id="chunk_1", metadata={'chunk_type': 'fixed'}),
            Chunk(content="Second chunk", chunk_id="chunk_2", metadata={'chunk_type': 'fixed'}),
            Chunk(content="Third chunk", chunk_id="chunk_3", metadata={'chunk_type': 'sentence'})
        ]
        
        stats = ChunkValidator.get_chunk_statistics(chunks)
        
        assert stats['total_chunks'] == 3
        assert stats['total_content_length'] > 0
        assert stats['avg_chunk_length'] > 0
        assert 'fixed' in stats['chunk_types']
        assert 'sentence' in stats['chunk_types']
        assert 'chunk_type' in stats['metadata_keys']
    
    def test_suggest_improvements(self):
        """Test improvement suggestions."""
        # Create a validation result with issues
        validation_result = {
            'is_valid': False,
            'overall_score': 60,
            'chunk_results': [
                {'result': {'is_valid': False}, 'chunk_id': 'chunk_1'},
                {'result': {'is_valid': True}, 'chunk_id': 'chunk_2'}
            ],
            'overlap_analysis': {
                'analysis': {'overlap_detected': True}
            },
            'summary': {'avg_chunk_length': 1500}
        }
        
        suggestions = ChunkValidator.suggest_improvements(validation_result)
        
        # Should have suggestions for invalid chunks
        assert len(suggestions) > 0
        assert 'Fix validation errors before proceeding' in suggestions


class TestErrorHandling:
    """Comprehensive tests for error handling."""
    
    def test_chunking_error_handling(self):
        """Test handling of chunking errors."""
        with pytest.raises(ChunkingError):
            raise ChunkingError("Test chunking error")
    
    def test_invalid_config_error_handling(self):
        """Test handling of invalid configuration errors."""
        with pytest.raises(InvalidConfigError):
            raise InvalidConfigError("Test config error")
    
    def test_tokenizer_error_handling(self):
        """Test handling of tokenizer errors."""
        with pytest.raises(TokenizerError):
            raise TokenizerError("Test tokenizer error")
    
    def test_semantic_model_error_handling(self):
        """Test handling of semantic model errors."""
        with pytest.raises(SemanticModelError):
            raise SemanticModelError("Test semantic model error")
    
    def test_structure_parsing_error_handling(self):
        """Test handling of structure parsing errors."""
        with pytest.raises(StructureParsingError):
            raise StructureParsingError("Test structure parsing error")
    
    def test_invalid_input_handling(self):
        """Test handling of invalid input."""
        chunker = FixedSizeChunker()
        
        # Test with None input
        with pytest.raises(ValueError):
            chunker.chunk(None)
        
        # Test with non-string input
        with pytest.raises(ValueError):
            chunker.chunk(123)
    
    def test_invalid_parameters(self):
        """Test handling of invalid parameters."""
        # Test negative chunk size
        with pytest.raises(ValueError):
            FixedSizeChunker(chunk_size=-1)
        
        # Test negative overlap
        with pytest.raises(ValueError):
            FixedSizeChunker(overlap=-1)
        
        # Test overlap larger than chunk size
        with pytest.raises(ValueError):
            FixedSizeChunker(chunk_size=10, overlap=15)


class TestIntegration:
    """Integration tests for the complete package."""
    
    def test_end_to_end_chunking_pipeline(self):
        """Test complete chunking pipeline."""
        text = "This is a test document. It contains multiple sentences. We will test the complete pipeline."
        
        # Create chunker
        chunker = FixedSizeChunker(chunk_size=30, overlap=5)
        chunks = chunker.chunk(text)
        
        # Validate chunks
        validator = ChunkValidator()
        validation_result = validator.validate_chunks(chunks)
        
        # Process text
        processor = TextProcessor()
        cleaned_text = processor.clean_text(text)
        
        # All operations should complete successfully
        assert len(chunks) > 0
        assert validation_result['is_valid'] is True
        assert len(cleaned_text) > 0
    
    def test_multiple_chunker_comparison(self):
        """Test comparison of different chunkers on same text."""
        text = "This is a test text. It has multiple sentences. We will compare different chunkers."
        
        # Test different chunkers
        fixed_chunker = FixedSizeChunker(chunk_size=20, overlap=5)
        sentence_chunker = SentenceBasedChunker()
        
        fixed_chunks = fixed_chunker.chunk(text)
        sentence_chunks = sentence_chunker.chunk(text)
        
        # Both should produce valid chunks
        assert len(fixed_chunks) > 0
        assert len(sentence_chunks) > 0
        
        # Should produce different results
        assert len(fixed_chunks) != len(sentence_chunks) or fixed_chunks != sentence_chunks
    
    def test_batch_processing(self):
        """Test batch processing of multiple texts."""
        texts = [
            "First document with some content.",
            "Second document with different content.",
            "Third document for testing."
        ]
        
        chunker = FixedSizeChunker(chunk_size=15, overlap=3)
        all_chunks = []
        
        for text in texts:
            chunks = chunker.chunk(text)
            all_chunks.extend(chunks)
        
        # Should process all texts
        assert len(all_chunks) > 0
        
        # Validate all chunks
        validator = ChunkValidator()
        validation_result = validator.validate_chunks(all_chunks)
        
        assert validation_result['is_valid'] is True


class TestPerformance:
    """Performance tests for the package."""
    
    def test_large_text_processing(self):
        """Test processing of large text."""
        # Create large text
        large_text = "This is a test sentence. " * 1000
        
        chunker = FixedSizeChunker(chunk_size=100, overlap=10)
        chunks = chunker.chunk(large_text)
        
        # Should handle large text efficiently
        assert len(chunks) > 0
        assert all(len(chunk.content) <= 100 for chunk in chunks)
    
    def test_memory_usage(self):
        """Test memory usage with large datasets."""
        # Create multiple large texts
        texts = ["Large text content. " * 500 for _ in range(10)]
        
        chunker = FixedSizeChunker(chunk_size=50, overlap=5)
        
        for text in texts:
            chunks = chunker.chunk(text)
            # Should not cause memory issues
            assert len(chunks) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
