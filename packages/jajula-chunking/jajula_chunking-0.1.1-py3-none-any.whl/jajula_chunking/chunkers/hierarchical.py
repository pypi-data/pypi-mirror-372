"""Hierarchical chunking implementation."""

from typing import List, Dict, Any, Optional
from .base import BaseChunker, Chunk


class HierarchicalChunk(Chunk):
    """Represents a hierarchical chunk with parent-child relationships."""
    
    def __init__(self, content: str, chunk_id: str, level: int = 0, 
                 parent_id: Optional[str] = None, children: List[str] = None,
                 **kwargs):
        """Initialize hierarchical chunk."""
        super().__init__(content, chunk_id, **kwargs)
        self.level = level
        self.parent_id = parent_id
        self.children = children or []
        self.metadata['chunk_type'] = 'hierarchical'
        self.metadata['level'] = level
        self.metadata['parent_id'] = parent_id
        self.metadata['children'] = self.children


class HierarchicalChunker(BaseChunker):
    """Creates hierarchical chunks with multiple levels of granularity."""
    
    def __init__(self, levels: List[Dict[str, Any]] = None, 
                 overlap: int = 100, **kwargs):
        """
        Initialize hierarchical chunker.
        
        Args:
            levels: List of level configurations
            overlap: Number of overlapping characters between levels
        """
        super().__init__(**kwargs)
        self.overlap = overlap
        
        if levels is None:
            # Default hierarchical levels
            self.levels = [
                {'name': 'document', 'max_size': 10000, 'chunker': 'paragraph'},
                {'name': 'section', 'max_size': 3000, 'chunker': 'sentence'},
                {'name': 'paragraph', 'max_size': 1000, 'chunker': 'fixed'},
                {'name': 'sentence', 'max_size': 200, 'chunker': 'word'}
            ]
        else:
            self.levels = levels
    
    def chunk(self, text: str) -> List[HierarchicalChunk]:
        """Create hierarchical chunks."""
        self._validate_input(text)
        
        # Start with document-level chunking
        document_chunks = self._create_level_chunks(text, self.levels[0], None)
        
        # Build hierarchy recursively
        hierarchical_chunks = []
        for doc_chunk in document_chunks:
            hierarchy = self._build_hierarchy(doc_chunk, 0)
            hierarchical_chunks.extend(hierarchy)
        
        return hierarchical_chunks
    
    def _create_level_chunks(self, text: str, level_config: Dict[str, Any], 
                            parent_id: Optional[str]) -> List[Chunk]:
        """Create chunks for a specific level."""
        chunker_type = level_config['chunker']
        max_size = level_config['max_size']
        
        if chunker_type == 'paragraph':
            from .paragraph_based import ParagraphBasedChunker
            chunker = ParagraphBasedChunker(max_paragraphs=1, overlap_paragraphs=0)
        elif chunker_type == 'sentence':
            from .sentence_based import SentenceBasedChunker
            chunker = SentenceBasedChunker(max_sentences=1, overlap_sentences=0)
        elif chunker_type == 'fixed':
            from .fixed_size import FixedSizeChunker
            chunker = FixedSizeChunker(chunk_size=max_size, overlap=self.overlap)
        elif chunker_type == 'word':
            # Simple word-based chunking
            words = text.split()
            chunks = []
            current_chunk = []
            current_size = 0
            
            for word in words:
                word_size = len(word) + 1  # +1 for space
                if current_size + word_size > max_size and current_chunk:
                    chunk_content = ' '.join(current_chunk)
                    chunk = Chunk(
                        content=chunk_content,
                        chunk_id=self._get_next_id(),
                        metadata={'chunk_type': 'word_based', 'word_count': len(current_chunk)}
                    )
                    chunks.append(chunk)
                    current_chunk = [word]
                    current_size = word_size
                else:
                    current_chunk.append(word)
                    current_size += word_size
            
            if current_chunk:
                chunk_content = ' '.join(current_chunk)
                chunk = Chunk(
                    content=chunk_content,
                    chunk_id=self._get_next_id(),
                    metadata={'chunk_type': 'word_based', 'word_count': len(current_chunk)}
                )
                chunks.append(chunk)
            
            return chunks
        else:
            # Default to fixed-size chunking
            from .fixed_size import FixedSizeChunker
            chunker = FixedSizeChunker(chunk_size=max_size, overlap=self.overlap)
        
        return chunker.chunk(text)
    
    def _build_hierarchy(self, parent_chunk: Chunk, level_index: int) -> List[HierarchicalChunk]:
        """Build hierarchical structure for a chunk."""
        if level_index >= len(self.levels) - 1:
            # Leaf level - create hierarchical chunk
            return [HierarchicalChunk(
                content=parent_chunk.content,
                chunk_id=parent_chunk.chunk_id,
                level=level_index,
                parent_id=None,  # Will be set by parent
                metadata=parent_chunk.metadata.copy()
            )]
        
        # Create sub-chunks for this level
        level_config = self.levels[level_index + 1]
        sub_chunks = self._create_level_chunks(parent_chunk.content, level_config, parent_chunk.chunk_id)
        
        # Create hierarchical chunk for current level
        hierarchical_chunk = HierarchicalChunk(
            content=parent_chunk.content,
            chunk_id=parent_chunk.chunk_id,
            level=level_index,
            parent_id=None,  # Will be set by parent
            children=[chunk.chunk_id for chunk in sub_chunks],
            metadata=parent_chunk.metadata.copy()
        )
        
        # Recursively build hierarchy for sub-chunks
        all_chunks = [hierarchical_chunk]
        for sub_chunk in sub_chunks:
            sub_hierarchy = self._build_hierarchy(sub_chunk, level_index + 1)
            # Set parent_id for sub-chunks
            for sub_hierarchical in sub_hierarchy:
                sub_hierarchical.parent_id = hierarchical_chunk.chunk_id
            all_chunks.extend(sub_hierarchy)
        
        return all_chunks
    
    def get_hierarchy_tree(self, chunks: List[HierarchicalChunk]) -> Dict[str, Any]:
        """Get hierarchical tree structure."""
        # Group chunks by level
        chunks_by_level = {}
        for chunk in chunks:
            level = chunk.level
            if level not in chunks_by_level:
                chunks_by_level[level] = []
            chunks_by_level[level].append(chunk)
        
        # Build tree structure
        tree = {
            'levels': sorted(chunks_by_level.keys()),
            'chunks_by_level': chunks_by_level,
            'relationships': self._extract_relationships(chunks)
        }
        
        return tree
    
    def _extract_relationships(self, chunks: List[HierarchicalChunk]) -> Dict[str, List[str]]:
        """Extract parent-child relationships."""
        relationships = {}
        for chunk in chunks:
            if chunk.parent_id:
                if chunk.parent_id not in relationships:
                    relationships[chunk.parent_id] = []
                relationships[chunk.parent_id].append(chunk.chunk_id)
        return relationships
    
    def get_chunks_at_level(self, chunks: List[HierarchicalChunk], level: int) -> List[HierarchicalChunk]:
        """Get all chunks at a specific level."""
        return [chunk for chunk in chunks if chunk.level == level]
    
    def get_leaf_chunks(self, chunks: List[HierarchicalChunk]) -> List[HierarchicalChunk]:
        """Get all leaf chunks (no children)."""
        return [chunk for chunk in chunks if not chunk.children]
    
    def get_root_chunks(self, chunks: List[HierarchicalChunk]) -> List[HierarchicalChunk]:
        """Get all root chunks (no parent)."""
        return [chunk for chunk in chunks if chunk.parent_id is None]

