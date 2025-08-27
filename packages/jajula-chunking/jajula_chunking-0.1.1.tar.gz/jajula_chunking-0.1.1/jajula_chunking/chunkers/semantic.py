"""Semantic chunking implementation."""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize
from typing import List, Optional
from .base import BaseChunker, Chunk
from ..exceptions import SemanticModelError
import nltk


class SemanticChunker(BaseChunker):
    """Chunks text based on semantic similarity."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', 
                 similarity_threshold: float = 0.5,
                 max_chunk_size: int = 1000,
                 min_sentences_per_chunk: int = 1, **kwargs):
        """
        Initialize semantic chunker.
        
        Args:
            model_name: Sentence transformer model name
            similarity_threshold: Similarity threshold for splitting
            max_chunk_size: Maximum chunk size in characters
            min_sentences_per_chunk: Minimum sentences per chunk
        """
        super().__init__(**kwargs)
        self.similarity_threshold = similarity_threshold
        self.max_chunk_size = max_chunk_size
        self.min_sentences_per_chunk = min_sentences_per_chunk
        
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            raise SemanticModelError(f"Failed to load model {model_name}: {e}")
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
    
    def chunk(self, text: str) -> List[Chunk]:
        """Chunk text based on semantic similarity."""
        self._validate_input(text)
        
        sentences = sent_tokenize(text)
        if len(sentences) <= 1:
            return [Chunk(
                content=text,
                chunk_id=self._get_next_id(),
                metadata={'chunk_type': 'semantic', 'sentence_count': len(sentences)}
            )]
        
        try:
            embeddings = self.model.encode(sentences)
        except Exception as e:
            raise SemanticModelError(f"Embedding generation failed: {e}")
        
        # Calculate similarities between consecutive sentences
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
            similarities.append(sim)
        
        # Find split points
        split_points = [0]
        for i, sim in enumerate(similarities):
            if sim < self.similarity_threshold:
                split_points.append(i + 1)
        split_points.append(len(sentences))
        
        # Create chunks
        chunks = []
        for i in range(len(split_points) - 1):
            start_idx = split_points[i]
            end_idx = split_points[i + 1]
            
            if end_idx - start_idx < self.min_sentences_per_chunk:
                continue
                
            chunk_sentences = sentences[start_idx:end_idx]
            chunk_content = ' '.join(chunk_sentences)
            
            # Split large chunks if needed
            if len(chunk_content) > self.max_chunk_size:
                sub_chunks = self._split_large_chunk(chunk_sentences)
                for sub_chunk_content in sub_chunks:
                    chunk = Chunk(
                        content=sub_chunk_content,
                        chunk_id=self._get_next_id(),
                        metadata={
                            'chunk_type': 'semantic',
                            'similarity_threshold': self.similarity_threshold,
                            'is_sub_chunk': True
                        }
                    )
                    chunks.append(chunk)
            else:
                chunk = Chunk(
                    content=chunk_content,
                    chunk_id=self._get_next_id(),
                    metadata={
                        'chunk_type': 'semantic',
                        'sentence_count': len(chunk_sentences),
                        'similarity_threshold': self.similarity_threshold
                    }
                )
                chunks.append(chunk)
        
        return chunks
    
    def _split_large_chunk(self, sentences: List[str]) -> List[str]:
        """Split large semantic chunks into smaller ones."""
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            if current_size + sentence_size > self.max_chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_size = sentence_size
            else:
                current_chunk.append(sentence)
                current_size += sentence_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

