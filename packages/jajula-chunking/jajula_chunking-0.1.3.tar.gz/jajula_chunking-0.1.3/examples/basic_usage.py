#!/usr/bin/env python3
"""
Basic usage examples for Jajula Chunking library.

This script demonstrates the basic usage of different chunking strategies.
"""

from jajula_chunking import (
    FixedSizeChunker,
    SentenceBasedChunker,
    ParagraphBasedChunker,
    SemanticChunker,
    TokenBasedChunker,
    RecursiveChunker,
    AdaptiveChunker,
    TextProcessor,
    ChunkValidator
)


def main():
    """Main function demonstrating basic usage."""
    print("🚀 Jajula Chunking - Basic Usage Examples\n")
    
    # Sample text for chunking
    sample_text = """
    Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language, in particular how to program computers to process and analyze large amounts of natural language data.

    Challenges in natural language processing frequently involve speech recognition, natural language understanding, and natural language generation. The field has seen significant advances in recent years, particularly with the development of large language models and transformer architectures.

    Applications of NLP include machine translation, sentiment analysis, question answering, text summarization, and chatbots. These applications are becoming increasingly important in modern technology and are used in various industries including healthcare, finance, and customer service.
    """
    
    print("📝 Sample Text:")
    print(f"Length: {len(sample_text)} characters")
    print(f"Words: {TextProcessor.count_words(sample_text)}")
    print(f"Sentences: {len(TextProcessor.extract_sentences(sample_text))}")
    print(f"Paragraphs: {len(TextProcessor.extract_paragraphs(sample_text))}")
    print("-" * 80)
    
    # 1. Fixed Size Chunking
    print("\n🔧 1. Fixed Size Chunking")
    fixed_chunker = FixedSizeChunker(chunk_size=200, overlap=50)
    fixed_chunks = fixed_chunker.chunk(sample_text)
    
    print(f"Created {len(fixed_chunks)} chunks:")
    for i, chunk in enumerate(fixed_chunks):
        print(f"  Chunk {i+1}: {len(chunk.content)} chars - {chunk.content[:50]}...")
    
    # 2. Sentence-Based Chunking
    print("\n🔧 2. Sentence-Based Chunking")
    sentence_chunker = SentenceBasedChunker(max_sentences=2, overlap_sentences=1)
    sentence_chunks = sentence_chunker.chunk(sample_text)
    
    print(f"Created {len(sentence_chunks)} chunks:")
    for i, chunk in enumerate(sentence_chunks):
        sentence_count = chunk.metadata.get('sentence_count', 0)
        print(f"  Chunk {i+1}: {sentence_count} sentences - {chunk.content[:60]}...")
    
    # 3. Paragraph-Based Chunking
    print("\n🔧 3. Paragraph-Based Chunking")
    paragraph_chunker = ParagraphBasedChunker(max_paragraphs=2, overlap_paragraphs=1)
    paragraph_chunks = paragraph_chunker.chunk(sample_text)
    
    print(f"Created {len(paragraph_chunks)} chunks:")
    for i, chunk in enumerate(paragraph_chunks):
        paragraph_count = chunk.metadata.get('paragraph_count', 0)
        print(f"  Chunk {i+1}: {paragraph_count} paragraphs - {chunk.content[:60]}...")
    
    # 4. Token-Based Chunking
    print("\n🔧 4. Token-Based Chunking")
    try:
        token_chunker = TokenBasedChunker(max_tokens=50, overlap_tokens=5)
        token_chunks = token_chunker.chunk(sample_text)
        
        print(f"Created {len(token_chunks)} chunks:")
        for i, chunk in enumerate(token_chunks):
            token_count = chunk.metadata.get('token_count', 0)
            print(f"  Chunk {i+1}: {token_count} tokens - {chunk.content[:60]}...")
    except Exception as e:
        print(f"  Token-based chunking failed: {e}")
        print("  (This requires tiktoken to be properly installed)")
    
    # 5. Recursive Chunking
    print("\n🔧 5. Recursive Chunking")
    recursive_chunker = RecursiveChunker(chunk_size=150)
    recursive_chunks = recursive_chunker.chunk(sample_text)
    
    print(f"Created {len(recursive_chunks)} chunks:")
    for i, chunk in enumerate(recursive_chunks):
        print(f"  Chunk {i+1}: {len(chunk.content)} chars - {chunk.content[:50]}...")
    
    # 6. Adaptive Chunking
    print("\n🔧 6. Adaptive Chunking")
    adaptive_chunker = AdaptiveChunker(max_chunk_size=300, enable_semantic=False)
    adaptive_chunks = adaptive_chunker.chunk(sample_text)
    
    print(f"Created {len(adaptive_chunks)} chunks:")
    for i, chunk in enumerate(adaptive_chunks):
        strategy = chunk.metadata.get('adaptive_strategy', 'unknown')
        print(f"  Chunk {i+1}: {strategy} strategy - {chunk.content[:50]}...")
    
    # 7. Semantic Chunking (if available)
    print("\n🔧 7. Semantic Chunking")
    try:
        semantic_chunker = SemanticChunker(similarity_threshold=0.7, max_chunk_size=400)
        semantic_chunks = semantic_chunker.chunk(sample_text)
        
        print(f"Created {len(semantic_chunks)} chunks:")
        for i, chunk in enumerate(semantic_chunks):
            similarity = chunk.metadata.get('similarity_threshold', 'unknown')
            print(f"  Chunk {i+1}: similarity {similarity} - {chunk.content[:50]}...")
    except Exception as e:
        print(f"  Semantic chunking failed: {e}")
        print("  (This requires sentence-transformers and torch to be properly installed)")
    
    # 8. Chunk Validation
    print("\n🔧 8. Chunk Validation")
    all_chunks = fixed_chunks + sentence_chunks + paragraph_chunks
    
    print(f"Validating {len(all_chunks)} chunks...")
    validation_result = ChunkValidator.validate_chunks(all_chunks)
    
    print(f"  Overall valid: {validation_result['is_valid']}")
    print(f"  Overall score: {validation_result['overall_score']:.1f}/100")
    print(f"  Valid chunks: {validation_result['summary']['valid_chunks']}")
    print(f"  Invalid chunks: {validation_result['summary']['invalid_chunks']}")
    
    if validation_result['warnings']:
        print(f"  Warnings: {len(validation_result['warnings'])}")
        for warning in validation_result['warnings'][:3]:  # Show first 3 warnings
            print(f"    - {warning}")
    
    # 9. Text Processing Utilities
    print("\n🔧 9. Text Processing Utilities")
    cleaned_text = TextProcessor.clean_text(sample_text, remove_html=True, normalize_whitespace=True)
    stats = TextProcessor.get_text_statistics(cleaned_text)
    keywords = TextProcessor.extract_keywords(cleaned_text, max_keywords=5)
    
    print(f"  Cleaned text length: {len(cleaned_text)} characters")
    print(f"  Language detected: {TextProcessor.detect_language(cleaned_text)}")
    print(f"  Top keywords: {', '.join(keywords)}")
    
    # 10. Strategy Recommendation
    print("\n🔧 10. Strategy Recommendation")
    recommendation = adaptive_chunker.get_strategy_recommendation(sample_text)
    
    print(f"  Recommended strategy: {recommendation['recommended_strategy']}")
    print(f"  Reasoning: {recommendation['reasoning']}")
    print(f"  Alternative strategies: {', '.join(recommendation['alternative_strategies'])}")
    
    print("\n✅ Basic usage examples completed!")
    print("\n💡 Tips:")
    print("  - Use FixedSizeChunker for consistent chunk sizes")
    print("  - Use SentenceBasedChunker for semantic coherence")
    print("  - Use ParagraphBasedChunker for document structure")
    print("  - Use AdaptiveChunker for automatic strategy selection")
    print("  - Always validate your chunks with ChunkValidator")
    print("  - Use TextProcessor for text preprocessing")


if __name__ == "__main__":
    main()



