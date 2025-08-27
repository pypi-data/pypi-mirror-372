#!/usr/bin/env python3
"""
Advanced usage examples for Jajula Chunking library.

This script demonstrates advanced features and complex chunking scenarios.
"""

import json
from jajula_chunking import (
    HierarchicalChunker,
    StructureBasedChunker,
    AdaptiveChunker,
    TextProcessor,
    ChunkValidator
)
from jajula_chunking.chunkers.base import Chunk


def demonstrate_hierarchical_chunking():
    """Demonstrate hierarchical chunking with custom levels."""
    print("🌳 Hierarchical Chunking Example")
    print("=" * 50)
    
    # Sample document with clear structure
    document = """
    # Introduction to Machine Learning
    
    Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions without being explicitly programmed.
    
    ## Supervised Learning
    
    Supervised learning involves training a model on labeled data. The model learns to map inputs to outputs based on examples.
    
    ### Classification
    Classification tasks involve categorizing data into predefined classes. Examples include spam detection and image recognition.
    
    ### Regression
    Regression tasks involve predicting continuous values. Examples include house price prediction and stock price forecasting.
    
    ## Unsupervised Learning
    
    Unsupervised learning finds hidden patterns in unlabeled data without predefined outputs.
    
    ### Clustering
    Clustering groups similar data points together. Examples include customer segmentation and document categorization.
    
    ### Dimensionality Reduction
    Dimensionality reduction reduces the number of features while preserving important information.
    
    ## Deep Learning
    
    Deep learning uses neural networks with multiple layers to learn complex patterns in data.
    
    ### Neural Networks
    Neural networks are composed of interconnected nodes that process information in layers.
    
    ### Convolutional Neural Networks
    CNNs are specialized for processing grid-like data such as images.
    
    ### Recurrent Neural Networks
    RNNs are designed for sequential data such as text and time series.
    """
    
    # Custom hierarchical levels
    custom_levels = [
        {'name': 'document', 'max_size': 5000, 'chunker': 'paragraph'},
        {'name': 'section', 'max_size': 2000, 'chunker': 'sentence'},
        {'name': 'subsection', 'max_size': 1000, 'chunker': 'fixed'},
        {'name': 'paragraph', 'max_size': 500, 'chunker': 'sentence'}
    ]
    
    chunker = HierarchicalChunker(levels=custom_levels, overlap=100)
    hierarchical_chunks = chunker.chunk(document)
    
    print(f"Created {len(hierarchical_chunks)} hierarchical chunks")
    
    # Group chunks by level
    chunks_by_level = {}
    for chunk in hierarchical_chunks:
        level = chunk.metadata.get('level', 0)
        if level not in chunks_by_level:
            chunks_by_level[level] = []
        chunks_by_level[level].append(chunk)
    
    # Display hierarchy
    for level in sorted(chunks_by_level.keys()):
        level_chunks = chunks_by_level[level]
        print(f"\nLevel {level} ({len(level_chunks)} chunks):")
        for i, chunk in enumerate(level_chunks):
            content_preview = chunk.content[:60].replace('\n', ' ')
            print(f"  {i+1}. {content_preview}...")
    
    # Get hierarchy tree
    tree = chunker.get_hierarchy_tree(hierarchical_chunks)
    print(f"\nHierarchy tree has {len(tree['levels'])} levels")
    print(f"Relationships: {len(tree['relationships'])} parent-child connections")
    
    return hierarchical_chunks


def demonstrate_structure_based_chunking():
    """Demonstrate structure-based chunking with different document types."""
    print("\n🏗️ Structure-Based Chunking Example")
    print("=" * 50)
    
    # HTML document
    html_document = """
    <html>
    <head><title>Sample Document</title></head>
    <body>
        <h1>Main Title</h1>
        <p>This is the first paragraph with some content.</p>
        <p>This is the second paragraph with different content.</p>
        
        <h2>Subsection</h2>
        <ul>
            <li>First list item</li>
            <li>Second list item</li>
            <li>Third list item</li>
        </ul>
        
        <div class="content">
            <p>This is content in a div container.</p>
            <p>Another paragraph in the same container.</p>
        </div>
    </body>
    </html>
    """
    
    # Markdown document
    markdown_document = """
    # Markdown Document
    
    This is a **markdown** document with various elements.
    
    ## Lists
    
    * Item 1
    * Item 2
    * Item 3
    
    ## Code
    
    ```python
    def hello_world():
        print("Hello, World!")
    ```
    
    ## Links
    
    [Visit our website](https://example.com)
    
    ## Emphasis
    
    *Italic text* and **bold text**
    """
    
    # Initialize chunker
    chunker = StructureBasedChunker(max_chunk_size=300, preserve_structure=True)
    
    # Chunk HTML
    print("HTML Document Chunking:")
    html_chunks = chunker.chunk(html_document)
    print(f"  Created {len(html_chunks)} chunks")
    
    for i, chunk in enumerate(html_chunks):
        element_types = chunk.metadata.get('element_types', [])
        element_count = chunk.metadata.get('element_count', 0)
        print(f"  Chunk {i+1}: {element_count} elements ({', '.join(element_types)})")
    
    # Chunk Markdown
    print("\nMarkdown Document Chunking:")
    markdown_chunks = chunker.chunk(markdown_document)
    print(f"  Created {len(markdown_chunks)} chunks")
    
    for i, chunk in enumerate(markdown_chunks):
        element_types = chunk.metadata.get('element_types', [])
        element_count = chunk.metadata.get('element_count', 0)
        print(f"  Chunk {i+1}: {element_count} elements ({', '.join(element_types)})")
    
    return html_chunks + markdown_chunks


def demonstrate_adaptive_chunking():
    """Demonstrate adaptive chunking with different text types."""
    print("\n🧠 Adaptive Chunking Example")
    print("=" * 50)
    
    # Different types of text
    text_samples = {
        'technical_document': """
        The implementation of the RESTful API follows the OpenAPI 3.0 specification. 
        The API endpoints are designed using resource-oriented architecture principles.
        Authentication is handled via JWT tokens with OAuth 2.0 flow.
        Rate limiting is implemented using Redis with sliding window algorithm.
        The database schema follows third normal form with proper indexing strategies.
        """,
        
        'narrative_text': """
        Once upon a time, in a distant land, there lived a wise old wizard. 
        He spent his days studying ancient tomes and practicing magical arts.
        The villagers often came to him for advice and magical assistance.
        His knowledge of spells and potions was unmatched in the entire kingdom.
        """,
        
        'structured_data': """
        Product: Laptop Computer
        Brand: TechCorp
        Model: XPS-15
        Specifications:
        - Processor: Intel i7-10700K
        - Memory: 16GB DDR4
        - Storage: 512GB SSD
        - Display: 15.6" 4K UHD
        
        Price: $1,299.99
        Availability: In Stock
        """,
        
        'code_documentation': """
        ```python
        class DataProcessor:
            def __init__(self, config: Dict[str, Any]):
                self.config = config
                self.logger = logging.getLogger(__name__)
            
            def process_data(self, data: List[Dict]) -> List[Dict]:
                processed_data = []
                for item in data:
                    try:
                        processed_item = self._transform_item(item)
                        processed_data.append(processed_item)
                    except Exception as e:
                        self.logger.error(f"Error processing item: {e}")
                return processed_data
        ```
        """
    }
    
    # Initialize adaptive chunker
    chunker = AdaptiveChunker(max_chunk_size=400, enable_semantic=True)
    
    for text_type, text in text_samples.items():
        print(f"\n{text_type.replace('_', ' ').title()}:")
        
        # Get strategy recommendation
        recommendation = chunker.get_strategy_recommendation(text)
        print(f"  Recommended strategy: {recommendation['recommended_strategy']}")
        print(f"  Reasoning: {recommendation['reasoning']}")
        
        # Analyze text characteristics
        analysis = recommendation['text_analysis']
        print(f"  Text length: {analysis['length']} chars")
        print(f"  Technical terms: {analysis['technical_terms']}")
        print(f"  Code blocks: {analysis['code_blocks']}")
        print(f"  Readability score: {analysis['readability_score']:.1f}")
        
        # Create chunks
        chunks = chunker.chunk(text)
        print(f"  Created {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            strategy = chunk.metadata.get('adaptive_strategy', 'unknown')
            content_preview = chunk.content[:50].replace('\n', ' ')
            print(f"    Chunk {i+1} ({strategy}): {content_preview}...")


def demonstrate_custom_chunk_processing():
    """Demonstrate custom chunk processing and analysis."""
    print("\n🔧 Custom Chunk Processing Example")
    print("=" * 50)
    
    # Sample text
    text = """
    Artificial Intelligence (AI) is transforming industries across the globe. 
    Machine learning algorithms are being deployed in healthcare, finance, and transportation.
    Natural language processing enables computers to understand human language.
    Computer vision systems can identify objects and patterns in images.
    Robotics combines AI with mechanical systems for automation.
    """
    
    # Create chunks using different strategies
    from jajula_chunking import FixedSizeChunker, SentenceBasedChunker
    
    fixed_chunker = FixedSizeChunker(chunk_size=150, overlap=30)
    sentence_chunker = SentenceBasedChunker(max_sentences=2, overlap_sentences=1)
    
    fixed_chunks = fixed_chunker.chunk(text)
    sentence_chunks = sentence_chunker.chunk(text)
    
    all_chunks = fixed_chunks + sentence_chunks
    
    # Custom analysis
    print(f"Total chunks: {len(all_chunks)}")
    
    # Analyze chunk characteristics
    chunk_analysis = {
        'total_content_length': sum(len(chunk.content) for chunk in all_chunks),
        'avg_chunk_length': sum(len(chunk.content) for chunk in all_chunks) / len(all_chunks),
        'chunk_types': {},
        'content_overlap': 0,
        'quality_scores': []
    }
    
    # Count chunk types
    for chunk in all_chunks:
        chunk_type = chunk.metadata.get('chunk_type', 'unknown')
        chunk_analysis['chunk_types'][chunk_type] = chunk_analysis['chunk_types'].get(chunk_type, 0) + 1
    
    # Check for content overlap
    for i in range(len(all_chunks) - 1):
        for j in range(i + 1, len(all_chunks)):
            chunk1 = all_chunks[i].content.lower()
            chunk2 = all_chunks[j].content.lower()
            
            # Simple overlap detection
            words1 = set(chunk1.split())
            words2 = set(chunk2.split())
            
            if len(words1.intersection(words2)) > 3:  # More than 3 common words
                chunk_analysis['content_overlap'] += 1
    
    # Calculate quality scores
    for chunk in all_chunks:
        # Simple quality heuristic
        content = chunk.content
        quality_score = 100
        
        # Penalize very short chunks
        if len(content) < 50:
            quality_score -= 20
        
        # Penalize chunks with excessive punctuation
        if content.count('.') + content.count('!') + content.count('?') > len(content) / 20:
            quality_score -= 10
        
        # Bonus for chunks with good word variety
        words = content.split()
        if len(set(words)) / len(words) > 0.8:
            quality_score += 10
        
        chunk_analysis['quality_scores'].append(quality_score)
    
    # Display analysis
    print(f"Total content length: {chunk_analysis['total_content_length']} characters")
    print(f"Average chunk length: {chunk_analysis['avg_chunk_length']:.1f} characters")
    print(f"Chunk types: {chunk_analysis['chunk_types']}")
    print(f"Content overlap detected: {chunk_analysis['content_overlap']} pairs")
    print(f"Average quality score: {sum(chunk_analysis['quality_scores']) / len(chunk_analysis['quality_scores']):.1f}/100")
    
    # Validate chunks
    print("\nChunk Validation:")
    validation_result = ChunkValidator.validate_chunks(all_chunks)
    
    print(f"  Overall valid: {validation_result['is_valid']}")
    print(f"  Overall score: {validation_result['overall_score']:.1f}/100")
    
    if validation_result['warnings']:
        print(f"  Warnings: {len(validation_result['warnings'])}")
        for warning in validation_result['warnings'][:3]:
            print(f"    - {warning}")
    
    # Get improvement suggestions
    suggestions = ChunkValidator.suggest_improvements(validation_result)
    if suggestions:
        print(f"  Improvement suggestions: {len(suggestions)}")
        for suggestion in suggestions[:3]:
            print(f"    - {suggestion}")
    
    return all_chunks


def demonstrate_batch_processing():
    """Demonstrate batch processing of multiple documents."""
    print("\n📚 Batch Processing Example")
    print("=" * 50)
    
    # Sample documents
    documents = [
        {
            'id': 'doc_001',
            'title': 'Machine Learning Basics',
            'content': 'Machine learning is a subset of artificial intelligence...',
            'type': 'technical'
        },
        {
            'id': 'doc_002',
            'title': 'Story of the Little Prince',
            'content': 'Once upon a time, there was a little prince...',
            'type': 'narrative'
        },
        {
            'id': 'doc_003',
            'title': 'API Documentation',
            'content': 'The REST API provides endpoints for user management...',
            'type': 'technical'
        }
    ]
    
    # Initialize chunkers
    adaptive_chunker = AdaptiveChunker(max_chunk_size=300)
    structure_chunker = StructureBasedChunker(max_chunk_size=400)
    
    all_chunks = []
    processing_stats = {
        'total_documents': len(documents),
        'total_chunks': 0,
        'chunking_strategies': {},
        'processing_times': [],
        'quality_scores': []
    }
    
    print(f"Processing {len(documents)} documents...")
    
    for doc in documents:
        print(f"\nDocument: {doc['title']} ({doc['type']})")
        
        # Choose chunking strategy based on document type
        if doc['type'] == 'technical':
            chunker = adaptive_chunker
            strategy = 'adaptive'
        else:
            chunker = structure_chunker
            strategy = 'structure_based'
        
        # Process document
        chunks = chunker.chunk(doc['content'])
        
        # Add document metadata to chunks
        for chunk in chunks:
            chunk.metadata['document_id'] = doc['id']
            chunk.metadata['document_title'] = doc['title']
            chunk.metadata['document_type'] = doc['type']
            chunk.metadata['batch_processed'] = True
        
        all_chunks.extend(chunks)
        processing_stats['total_chunks'] += len(chunks)
        processing_stats['chunking_strategies'][strategy] = processing_stats['chunking_strategies'].get(strategy, 0) + 1
        
        print(f"  Created {len(chunks)} chunks using {strategy} strategy")
        
        # Validate chunks
        validation = ChunkValidator.validate_chunks(chunks)
        processing_stats['quality_scores'].append(validation['overall_score'])
        
        print(f"  Quality score: {validation['overall_score']:.1f}/100")
    
    # Overall statistics
    print(f"\nBatch Processing Complete!")
    print(f"Total chunks created: {processing_stats['total_chunks']}")
    print(f"Chunking strategies used: {processing_stats['chunking_strategies']}")
    print(f"Average quality score: {sum(processing_stats['quality_scores']) / len(processing_stats['quality_scores']):.1f}/100")
    
    # Export chunks to JSON for analysis
    chunks_data = []
    for chunk in all_chunks:
        chunk_data = {
            'chunk_id': chunk.chunk_id,
            'content': chunk.content,
            'metadata': chunk.metadata,
            'start_index': chunk.start_index,
            'end_index': chunk.end_index
        }
        chunks_data.append(chunk_data)
    
    # Save to file (optional)
    try:
        with open('batch_processed_chunks.json', 'w') as f:
            json.dump(chunks_data, f, indent=2)
        print("Chunks exported to 'batch_processed_chunks.json'")
    except Exception as e:
        print(f"Could not export chunks: {e}")
    
    return all_chunks


def main():
    """Main function demonstrating advanced features."""
    print("🚀 Jajula Chunking - Advanced Usage Examples\n")
    
    try:
        # Run all demonstrations
        hierarchical_chunks = demonstrate_hierarchical_chunking()
        structure_chunks = demonstrate_structure_based_chunking()
        demonstrate_adaptive_chunking()
        custom_chunks = demonstrate_custom_chunk_processing()
        batch_chunks = demonstrate_batch_processing()
        
        # Summary
        total_chunks = len(hierarchical_chunks) + len(structure_chunks) + len(custom_chunks) + len(batch_chunks)
        
        print(f"\n🎉 Advanced examples completed successfully!")
        print(f"Total chunks created across all examples: {total_chunks}")
        print("\n💡 Advanced Features Demonstrated:")
        print("  - Hierarchical chunking with custom levels")
        print("  - Structure-based chunking for HTML/Markdown")
        print("  - Adaptive chunking with intelligent strategy selection")
        print("  - Custom chunk processing and analysis")
        print("  - Batch processing of multiple documents")
        print("  - Advanced validation and quality assessment")
        print("  - Export and analysis capabilities")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
