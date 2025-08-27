"""Token-based chunking implementation."""

import tiktoken
from typing import List, Optional
from .base import BaseChunker, Chunk
from ..exceptions import TokenizerError


class TokenBasedChunker(BaseChunker):
    """Chunks text based on token count."""
    
    def __init__(self, max_tokens: int = 512, overlap_tokens: int = 50, 
                 model_name: str = "gpt-3.5-turbo", **kwargs):
        """
        Initialize token-based chunker.
        
        Args:
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Number of overlapping tokens
            model_name: OpenAI model name for tokenizer
        """
        super().__init__(**kwargs)
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.model_name = model_name
        
        try:
            self.tokenizer = tiktoken.encoding_for_model(model_name)
        except Exception as e:
            raise TokenizerError(f"Failed to initialize tokenizer for {model_name}: {e}")
    
    def chunk(self, text: str) -> List[Chunk]:
        """Chunk text based on token count."""
        self._validate_input(text)
        
        try:
            tokens = self.tokenizer.encode(text)
        except Exception as e:
            raise TokenizerError(f"Tokenization failed: {e}")
        
        if len(tokens) <= self.max_tokens:
            return [Chunk(
                content=text,
                chunk_id=self._get_next_id(),
                metadata={
                    'chunk_type': 'token_based',
                    'token_count': len(tokens),
                    'max_tokens': self.max_tokens
                }
            )]
        
        chunks = []
        start_idx = 0
        
        while start_idx < len(tokens):
            end_idx = min(start_idx + self.max_tokens, len(tokens))
            chunk_tokens = tokens[start_idx:end_idx]
            
            try:
                chunk_content = self.tokenizer.decode(chunk_tokens)
            except Exception as e:
                raise TokenizerError(f"Token decoding failed: {e}")
            
            if chunk_content.strip():
                chunk = Chunk(
                    content=chunk_content.strip(),
                    chunk_id=self._get_next_id(),
                    metadata={
                        'chunk_type': 'token_based',
                        'token_count': len(chunk_tokens),
                        'start_token': start_idx,
                        'end_token': end_idx - 1,
                        'max_tokens': self.max_tokens
                    }
                )
                chunks.append(chunk)
            
            # Move start index (accounting for overlap)
            start_idx = max(end_idx - self.overlap_tokens, start_idx + 1)
            
        return chunks
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            raise TokenizerError(f"Token counting failed: {e}")
    
    def get_tokenizer_info(self) -> dict:
        """Get information about the tokenizer."""
        return {
            'model_name': self.model_name,
            'max_tokens': self.max_tokens,
            'overlap_tokens': self.overlap_tokens
        }
