"""
Comprehensive logical tests for all chunkers.
Tests real-world scenarios and edge cases.
"""

import pytest
import time
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


class TestComprehensiveChunking:
    """Comprehensive tests for all chunking strategies."""
    
    @pytest.fixture
    def sample_texts(self):
        """Provide various sample texts for testing."""
        return {
            "short": "Hello world. This is a test.",
            "medium": """
            This is the first paragraph. It contains multiple sentences. 
            We will use this to test various chunking strategies.
            
            This is the second paragraph. It has different content.
            The chunkers should handle this properly.
            
            This is the third paragraph. It's longer than the others.
            We need to ensure proper chunking across boundaries.
            """,
            "long": """
            Artificial Intelligence (AI) is transforming the world around us. 
            From self-driving cars to virtual assistants, AI technologies are becoming increasingly prevalent in our daily lives. 
            Machine learning, a subset of AI, enables computers to learn and improve from experience without being explicitly programmed.
            
            Natural Language Processing (NLP) is another exciting field within AI. 
            It focuses on enabling computers to understand, interpret, and generate human language. 
            Applications include chatbots, language translation, and sentiment analysis.
            
            Computer Vision allows machines to interpret and understand visual information from the world. 
            This technology powers facial recognition systems, medical imaging analysis, and autonomous vehicles. 
            Deep learning models have significantly improved the accuracy of computer vision tasks.
            
            Robotics combines AI with mechanical engineering to create intelligent machines. 
            These robots can perform complex tasks in manufacturing, healthcare, and exploration. 
            The integration of AI makes robots more adaptable and intelligent.
            
            The future of AI holds immense potential. 
            As technology advances, we can expect more sophisticated AI systems. 
            However, it's crucial to address ethical concerns and ensure responsible AI development.
            """,
            "html": """
            <html>
            <head><title>Test Document</title></head>
            <body>
                <h1>Main Title</h1>
                <p>First paragraph with important information.</p>
                <h2>Subsection</h2>
                <p>Second paragraph with more details.</p>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                </ul>
                <h2>Another Section</h2>
                <p>Final paragraph with conclusions.</p>
            </body>
            </html>
            """,
            "markdown": """
            # Main Document
            
            ## Introduction
            This is an introduction paragraph.
            
            ## Section 1
            Content for section 1.
            
            ### Subsection 1.1
            More detailed content here.
            
            ## Section 2
            Content for section 2.
            
            ### Subsection 2.1
            Additional details.
            
            ## Conclusion
            Summary of the document.
            """,
            "code": """
            def process_data(data):
                \"\"\"Process the input data.\"\"\"
                result = []
                for item in data:
                    if item > 0:
                        result.append(item * 2)
                return result
            
            class DataProcessor:
                def __init__(self):
                    self.cache = {}
                
                def process(self, data):
                    \"\"\"Process data with caching.\"\"\"
                    if data in self.cache:
                        return self.cache[data]
                    
                    result = process_data(data)
                    self.cache[data] = result
                    return result
            """
        }
    
    def test_fixed_size_chunker_logical(self, sample_texts):
        """Test FixedSizeChunker with logical scenarios."""
        # Test 1: Normal chunking
        chunker = FixedSizeChunker(chunk_size=100, overlap=20)
        chunks = chunker.chunk(sample_texts["medium"])
        
        assert len(chunks) > 0
        assert all(len(chunk.content) <= 100 for chunk in chunks)
        
        # Test 2: Overlap functionality
        if len(chunks) > 1:
            chunk1 = chunks[0].content
            chunk2 = chunks[1].content
            # Check that there's some overlap
            assert any(word in chunk2 for word in chunk1.split()[-3:])
        
        # Test 3: Edge case - overlap larger than chunk_size
        chunker_edge = FixedSizeChunker(chunk_size=50, overlap=60)
        chunks_edge = chunker_edge.chunk(sample_texts["short"])
        assert len(chunks_edge) > 0  # Should not cause infinite loop
        
        # Test 4: Word boundary preservation
        chunker_word = FixedSizeChunker(chunk_size=30, overlap=5, split_on_word=True)
        chunks_word = chunker_word.chunk(sample_texts["medium"])
        for chunk in chunks_word:
            # Check that chunks don't start/end with partial words
            if chunk.content.strip():
                assert not chunk.content.startswith(' ')
                assert not chunk.content.endswith(' ')
    
    def test_sentence_based_chunker_logical(self, sample_texts):
        """Test SentenceBasedChunker with logical scenarios."""
        # Test 1: Normal sentence chunking
        chunker = SentenceBasedChunker(max_sentences=3, overlap_sentences=1)
        chunks = chunker.chunk(sample_texts["long"])
        
        assert len(chunks) > 0
        for chunk in chunks:
            sentence_count = chunk.metadata.get('sentence_count', 0)
            assert sentence_count <= 3
        
        # Test 2: Overlap verification
        if len(chunks) > 1:
            for i in range(len(chunks) - 1):
                chunk1 = chunks[i]
                chunk2 = chunks[i + 1]
                # Check metadata for overlap
                if 'end_sentence' in chunk1.metadata and 'start_sentence' in chunk2.metadata:
                    assert chunk1.metadata['end_sentence'] >= chunk2.metadata['start_sentence']
        
        # Test 3: Single sentence handling
        chunker_single = SentenceBasedChunker(max_sentences=5, overlap_sentences=0)
        chunks_single = chunker_single.chunk(sample_texts["short"])
        assert len(chunks_single) == 1
        
        # Test 4: Language-specific behavior
        chunker_eng = SentenceBasedChunker(language='english')
        chunks_eng = chunker_eng.chunk(sample_texts["medium"])
        assert len(chunks_eng) > 0
    
    def test_sentence_based_chunker_logical(self, sample_texts):
        """Test SentenceBasedChunker with logical scenarios."""
        # Test 1: Normal sentence chunking
        chunker = SentenceBasedChunker(max_sentences=3, overlap_sentences=1)
        chunks = chunker.chunk(sample_texts["long"])
        
        assert len(chunks) > 0
        for chunk in chunks:
            sentence_count = chunk.metadata.get('sentence_count', 0)
            assert sentence_count <= 3
        
        # Test 2: Overlap verification
        if len(chunks) > 1:
            for i in range(len(chunks) - 1):
                chunk1 = chunks[i]
                chunk2 = chunks[i + 1]
                # Check metadata for overlap
                if 'end_sentence' in chunk1.metadata and 'start_sentence' in chunk2.metadata:
                    assert chunk1.metadata['end_sentence'] >= chunk2.metadata['start_sentence']
        
        # Test 3: Single sentence handling
        chunker_single = SentenceBasedChunker(max_sentences=5, overlap_sentences=0)
        chunks_single = chunker_single.chunk(sample_texts["short"])
        assert len(chunks_single) == 1
        
        # Test 4: Language-specific behavior
        chunker_eng = SentenceBasedChunker(language='english')
        chunks_eng = chunker_eng.chunk(sample_texts["medium"])
        assert len(chunks_eng) > 0
    
    def test_paragraph_based_chunker_logical(self, sample_texts):
        """Test ParagraphBasedChunker with logical scenarios."""
        # Test 1: Normal paragraph chunking
        chunker = ParagraphBasedChunker(max_paragraphs=2, overlap_paragraphs=1)
        chunks = chunker.chunk(sample_texts["medium"])
        
        assert len(chunks) > 0
        for chunk in chunks:
            paragraph_count = chunk.metadata.get('paragraph_count', 0)
            assert paragraph_count <= 2
        
        # Test 2: Custom separators
        custom_separators = [r'\n---\n', r'\n\n']
        chunker_custom = ParagraphBasedChunker(
            max_paragraphs=1, 
            overlap_paragraphs=0,
            paragraph_separators=custom_separators
        )
        text_with_custom = "Para1\n---\nPara2\n\nPara3"
        chunks_custom = chunker_custom.chunk(text_with_custom)
        assert len(chunks_custom) >= 2  # Should create at least 2 chunks
        
        # Test 3: Empty paragraphs handling
        text_empty_paras = "Para1\n\n\nPara2\n\n\n\nPara3"
        chunker_empty = ParagraphBasedChunker(max_paragraphs=1, overlap_paragraphs=0)
        chunks_empty = chunker_empty.chunk(text_empty_paras)
        assert len(chunks_empty) == 3
    
    def test_token_based_chunker_logical(self, sample_texts):
        """Test TokenBasedChunker with logical scenarios."""
        # Test 1: Normal token chunking
        chunker = TokenBasedChunker(max_tokens=20, overlap_tokens=5)
        chunks = chunker.chunk(sample_texts["medium"])
        
        assert len(chunks) > 0
        for chunk in chunks:
            token_count = chunk.metadata.get('token_count', 0)
            assert token_count <= 20
        
        # Test 2: Token counting accuracy
        chunker_count = TokenBasedChunker()
        text = "This is a test sentence with multiple words."
        token_count = chunker_count.count_tokens(text)
        assert token_count > 0
        # Token count may differ from word count due to tokenization
        assert token_count >= len(text.split()) * 0.8  # Allow some variance
        
        # Test 3: Edge cases
        chunker_edge = TokenBasedChunker(max_tokens=1, overlap_tokens=0)
        chunks_edge = chunker_edge.chunk("Hello world")
        assert len(chunks_edge) == 2  # Should create 2 chunks for 2 words
        
        # Test 4: Large text handling
        chunker_large = TokenBasedChunker(max_tokens=100, overlap_tokens=10)
        chunks_large = chunker_large.chunk(sample_texts["long"])
        assert len(chunks_large) > 0
    
    def test_recursive_chunker_logical(self, sample_texts):
        """Test RecursiveChunker with logical scenarios."""
        # Test 1: Basic recursive splitting
        separators = ["\n", ". "]
        chunker = RecursiveChunker(separators=separators, chunk_size=50)
        chunks = chunker.chunk(sample_texts["code"])
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert len(chunk.content) <= 50
        
        # Test 2: Separator priority
        separators_priority = ["\n\n", "\n", ". "]
        chunker_priority = RecursiveChunker(separators=separators_priority, chunk_size=100)
        chunks_priority = chunker_priority.chunk(sample_texts["medium"])
        assert len(chunks_priority) > 0
        
        # Test 3: No separators found
        chunker_no_sep = RecursiveChunker(separators=["NONEXISTENT"], chunk_size=50)
        chunks_no_sep = chunker_no_sep.chunk(sample_texts["short"])
        assert len(chunks_no_sep) > 0  # Should fall back to character-based splitting
        
        # Test 4: Empty separators
        chunker_empty_sep = RecursiveChunker(separators=[], chunk_size=50)
        chunks_empty_sep = chunker_empty_sep.chunk(sample_texts["short"])
        assert len(chunks_empty_sep) > 0
    
    def test_structure_based_chunker_logical(self, sample_texts):
        """Test StructureBasedChunker with logical scenarios."""
        # Test 1: HTML structure parsing
        chunker_html = StructureBasedChunker(
            structure_type='html',
            max_chunk_size=200,
            preserve_structure=True
        )
        chunks_html = chunker_html.chunk(sample_texts["html"])
        
        assert len(chunks_html) > 0
        for chunk in chunks_html:
            assert chunk.metadata.get('chunk_type') == 'structure_based'
            assert 'element_count' in chunk.metadata
        
        # Test 2: Markdown structure parsing
        chunker_md = StructureBasedChunker(
            structure_type='markdown',
            max_chunk_size=150,
            preserve_structure=True
        )
        chunks_md = chunker_md.chunk(sample_texts["markdown"])
        
        assert len(chunks_md) > 0
        for chunk in chunks_md:
            assert chunk.metadata.get('chunk_type') == 'structure_based'
            # Markdown chunks may have different metadata structure
            assert any(key in chunk.metadata for key in ['element_count', 'element_type', 'paragraph_index'])
        
        # Test 3: Structure preservation
        chunker_preserve = StructureBasedChunker(
            structure_type='html',
            preserve_structure=True
        )
        chunks_preserve = chunker_preserve.chunk(sample_texts["html"])
        
        # Check that structure information is preserved
        for chunk in chunks_preserve:
            assert 'element_count' in chunk.metadata
            assert 'element_types' in chunk.metadata
    
    def test_semantic_chunker_logical(self, sample_texts):
        """Test SemanticChunker with logical scenarios."""
        # Test 1: Basic semantic chunking
        chunker = SemanticChunker(
            similarity_threshold=0.7,
            max_chunk_size=300,
            min_sentences_per_chunk=1
        )
        
        # Use a smaller text for faster testing
        text = sample_texts["short"] * 10
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.metadata.get('chunk_type') == 'semantic'
        
        # Test 2: Similarity threshold effect
        chunker_high = SemanticChunker(similarity_threshold=0.9)
        chunks_high = chunker_high.chunk(text)
        
        chunker_low = SemanticChunker(similarity_threshold=0.3)
        chunks_low = chunker_low.chunk(text)
        
        # Lower threshold should create fewer chunks (more grouping)
        assert len(chunks_low) <= len(chunks_high)
        
        # Test 3: Model loading
        assert hasattr(chunker, 'model')
        assert chunker.model is not None
    
    def test_hierarchical_chunker_logical(self, sample_texts):
        """Test HierarchicalChunker with logical scenarios."""
        # Test 1: Basic hierarchical chunking (use default levels)
        chunker = HierarchicalChunker()
        chunks = chunker.chunk(sample_texts["long"])
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert 'level' in chunk.metadata
            assert chunk.metadata['chunk_type'] == 'hierarchical'
        
        # Test 2: Custom level configuration
        custom_levels = [
            {'name': 'chapter', 'max_size': 2000, 'chunker': 'paragraph'},
            {'name': 'section', 'max_size': 500, 'chunker': 'sentence'}
        ]
        chunker_custom = HierarchicalChunker(levels=custom_levels)
        chunks_custom = chunker_custom.chunk(sample_texts["long"])
        
        for chunk in chunks_custom:
            assert chunk.metadata['chunk_type'] == 'hierarchical'
    
    def test_adaptive_chunker_logical(self, sample_texts):
        """Test AdaptiveChunker with logical scenarios."""
        # Test 1: Basic adaptive chunking
        chunker = AdaptiveChunker(
            strategies=['fixed_size', 'sentence_based', 'paragraph_based'],
            content_analysis=True
        )
        chunks = chunker.chunk(sample_texts["long"])
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert 'adaptive_strategy' in chunk.metadata
            assert chunk.metadata['adaptive_strategy'] in ['fixed_size', 'sentence_based', 'paragraph_based', 'semantic']
        
        # Test 2: Strategy selection
        chunker_strategies = AdaptiveChunker(
            strategies=['fixed_size', 'semantic'],
            content_analysis=True
        )
        chunks_strategies = chunker_strategies.chunk(sample_texts["medium"])
        
        for chunk in chunks_strategies:
            assert chunk.metadata['adaptive_strategy'] in ['fixed_size', 'semantic']
        
        # Test 3: Content analysis
        chunker_analysis = AdaptiveChunker(content_analysis=True)
        chunks_analysis = chunker_analysis.chunk(sample_texts["code"])
        
        for chunk in chunks_analysis:
            assert 'text_analysis' in chunk.metadata
    
    def test_performance_and_memory(self, sample_texts):
        """Test performance and memory usage."""
        # Test 1: Large text handling
        large_text = sample_texts["long"] * 10  # Make it very long
        
        start_time = time.time()
        chunker = FixedSizeChunker(chunk_size=500, overlap=50)
        chunks = chunker.chunk(large_text)
        end_time = time.time()
        
        # Should complete within reasonable time
        assert end_time - start_time < 10.0  # 10 seconds max
        assert len(chunks) > 0
        
        # Test 2: Memory efficiency
        chunker_memory = FixedSizeChunker(chunk_size=100, overlap=10)
        chunks_memory = chunker_memory.chunk(large_text)
        
        # Check that chunk sizes are reasonable
        total_content_length = sum(len(chunk.content) for chunk in chunks_memory)
        assert total_content_length <= len(large_text) * 1.5  # Allow some overhead
    
    def test_edge_cases_and_error_handling(self, sample_texts):
        """Test edge cases and error handling."""
        # Test 1: Very short text
        chunker = FixedSizeChunker(chunk_size=1000, overlap=0)  # No overlap for this test
        chunks = chunker.chunk("Hi")
        assert len(chunks) == 1
        assert chunks[0].content == "Hi"
        
        # Test 1b: Very short text with overlap (should create multiple chunks)
        chunker_overlap = FixedSizeChunker(chunk_size=1000, overlap=100)
        chunks_overlap = chunker_overlap.chunk("Hi")
        assert len(chunks_overlap) > 1  # Overlap should create multiple chunks
        
        # Test 2: Text with only whitespace
        with pytest.raises(ValueError):
            chunker.chunk("   \n\n\t   ")
        
        # Test 3: Very long words
        long_word_text = "This is a text with a verylongwordthatislongerthanthechunksize " * 5
        chunker_long = FixedSizeChunker(chunk_size=50, overlap=10, split_on_word=True)
        chunks_long = chunker_long.chunk(long_word_text)
        assert len(chunks_long) > 0
        
        # Test 4: Special characters
        special_text = "Text with special chars: @#$%^&*()_+{}|:<>?[]\\;'\",./"
        chunker_special = FixedSizeChunker(chunk_size=30, overlap=5)
        chunks_special = chunker_special.chunk(special_text)
        assert len(chunks_special) > 0
        
        # Test 5: Unicode text
        unicode_text = "Text with unicode: 你好世界 🌍 🚀"
        chunker_unicode = FixedSizeChunker(chunk_size=20, overlap=5)
        chunks_unicode = chunker_unicode.chunk(unicode_text)
        assert len(chunks_unicode) > 0
    
    def test_chunk_metadata_consistency(self, sample_texts):
        """Test that chunk metadata is consistent and useful."""
        chunker = FixedSizeChunker(chunk_size=100, overlap=20)
        chunks = chunker.chunk(sample_texts["medium"])
        
        for i, chunk in enumerate(chunks):
            # Check required metadata
            assert 'chunk_type' in chunk.metadata
            assert 'chunk_size' in chunk.metadata
            assert 'overlap' in chunk.metadata
            
            # Check chunk ID format
            assert chunk.chunk_id.startswith('fixedsizechunker_')
            assert chunk.chunk_id.endswith(str(i + 1))
            
            # Check indices
            assert chunk.start_index >= 0
            assert chunk.end_index > chunk.start_index
            assert chunk.end_index <= len(sample_texts["medium"])
            
            # Check content consistency
            assert chunk.content == sample_texts["medium"][chunk.start_index:chunk.end_index].strip()
    
    def test_chunk_size_and_split_all_functionality(self, sample_texts):
        """Test chunk size and split all functionality - the specific issue mentioned."""
        # Test 1: Very small chunk size with large overlap (the problematic case)
        chunker_small = FixedSizeChunker(chunk_size=22, overlap=50)
        text = "Your long text here..."
        chunks = chunker_small.chunk(text)
        
        # Should not cause MemoryError or infinite loop
        assert len(chunks) > 0
        assert len(chunks) <= len(text)  # Should not create more chunks than text length
        
        # Test 2: Chunk size smaller than overlap
        chunker_edge = FixedSizeChunker(chunk_size=10, overlap=20)
        chunks_edge = chunker_edge.chunk(text)
        assert len(chunks_edge) > 0
        
        # Test 3: Chunk size equals overlap
        chunker_equal = FixedSizeChunker(chunk_size=15, overlap=15)
        chunks_equal = chunker_equal.chunk(text)
        assert len(chunks_equal) > 0
        
        # Test 4: Zero overlap
        chunker_zero = FixedSizeChunker(chunk_size=20, overlap=0)
        chunks_zero = chunker_zero.chunk(text)
        assert len(chunks_zero) > 0
        
        # Test 5: Very large text with small chunks
        long_text = "This is a very long text. " * 100
        chunker_long = FixedSizeChunker(chunk_size=50, overlap=10)
        chunks_long = chunker_long.chunk(long_text)
        assert len(chunks_long) > 0
        
        # Verify chunk sizes are correct
        for chunk in chunks_long:
            assert len(chunk.content) <= 50
            assert chunk.metadata['chunk_size'] <= 50
    
    def test_integration_scenarios(self, sample_texts):
        """Test integration scenarios with multiple chunkers."""
        # Test 1: Pipeline chunking
        text = sample_texts["long"]
        
        # First chunk by sentences
        sentence_chunker = SentenceBasedChunker(max_sentences=3, overlap_sentences=1)
        sentence_chunks = sentence_chunker.chunk(text)
        
        # Then chunk each sentence chunk by size
        fixed_chunker = FixedSizeChunker(chunk_size=100, overlap=20)
        all_chunks = []
        
        for sentence_chunk in sentence_chunks:
            sub_chunks = fixed_chunker.chunk(sentence_chunk.content)
            all_chunks.extend(sub_chunks)
        
        assert len(all_chunks) > len(sentence_chunks)
        
        # Test 2: Mixed strategy chunking
        adaptive_chunker = AdaptiveChunker(
            strategies=['sentence_based', 'fixed_size'],
            content_analysis=True
        )
        mixed_chunks = adaptive_chunker.chunk(text)
        
        assert len(mixed_chunks) > 0
        strategies_used = set(chunk.metadata['adaptive_strategy'] for chunk in mixed_chunks)
        assert len(strategies_used) >= 1  # At least one strategy should be used


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
