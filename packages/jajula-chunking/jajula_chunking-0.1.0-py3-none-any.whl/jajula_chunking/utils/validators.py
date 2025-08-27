"""Validation utilities for chunking operations."""

import re
from typing import List, Dict, Any, Optional, Tuple
from ..chunkers.base import Chunk


class ChunkValidator:
    """Utility class for validating chunk quality and properties."""
    
    @staticmethod
    def validate_chunk(chunk: Chunk, min_length: int = 10, max_length: int = 10000) -> Dict[str, Any]:
        """
        Validate a single chunk.
        
        Args:
            chunk: Chunk to validate
            min_length: Minimum allowed chunk length
            max_length: Maximum allowed chunk length
            
        Returns:
            Validation results dictionary
        """
        if not isinstance(chunk, Chunk):
            return {
                'is_valid': False,
                'errors': ['Not a valid Chunk object'],
                'warnings': [],
                'score': 0.0
            }
        
        errors = []
        warnings = []
        score = 100.0
        
        # Check content
        if not chunk.content:
            errors.append('Chunk content is empty')
            score -= 50.0
        elif len(chunk.content.strip()) < min_length:
            errors.append(f'Chunk content too short ({len(chunk.content)} < {min_length})')
            score -= 30.0
        elif len(chunk.content) > max_length:
            errors.append(f'Chunk content too long ({len(chunk.content)} > {max_length})')
            score -= 20.0
        
        # Check chunk ID
        if not chunk.chunk_id:
            errors.append('Chunk ID is missing')
            score -= 20.0
        elif not isinstance(chunk.chunk_id, str):
            errors.append('Chunk ID must be a string')
            score -= 15.0
        
        # Check metadata
        if chunk.metadata is None:
            warnings.append('Chunk metadata is None')
            score -= 5.0
        elif not isinstance(chunk.metadata, dict):
            errors.append('Chunk metadata must be a dictionary')
            score -= 15.0
        
        # Check indices
        if chunk.start_index < 0:
            warnings.append('Start index is negative')
            score -= 5.0
        
        if chunk.end_index < chunk.start_index:
            errors.append('End index is before start index')
            score -= 20.0
        
        # Content quality checks
        content_quality = ChunkValidator._check_content_quality(chunk.content)
        if content_quality['warnings']:
            warnings.extend(content_quality['warnings'])
            score -= len(content_quality['warnings']) * 2.0
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'score': max(0.0, score),
            'content_quality': content_quality
        }
    
    @staticmethod
    def validate_chunks(chunks: List[Chunk], min_length: int = 10, 
                       max_length: int = 10000) -> Dict[str, Any]:
        """
        Validate a list of chunks.
        
        Args:
            chunks: List of chunks to validate
            min_length: Minimum allowed chunk length
            max_length: Maximum allowed chunk length
            
        Returns:
            Validation results dictionary
        """
        if not isinstance(chunks, list):
            return {
                'is_valid': False,
                'errors': ['Input must be a list of chunks'],
                'warnings': [],
                'overall_score': 0.0,
                'chunk_results': []
            }
        
        if not chunks:
            return {
                'is_valid': False,
                'errors': ['No chunks provided'],
                'warnings': [],
                'overall_score': 0.0,
                'chunk_results': []
            }
        
        chunk_results = []
        total_score = 0.0
        all_errors = []
        all_warnings = []
        
        for i, chunk in enumerate(chunks):
            result = ChunkValidator.validate_chunk(chunk, min_length, max_length)
            chunk_results.append({
                'index': i,
                'chunk_id': chunk.chunk_id if hasattr(chunk, 'chunk_id') else f'chunk_{i}',
                'result': result
            })
            
            total_score += result['score']
            all_errors.extend(result['errors'])
            all_warnings.extend(result['warnings'])
        
        overall_score = total_score / len(chunks)
        
        # Check for duplicate chunk IDs
        chunk_ids = [chunk.chunk_id for chunk in chunks if hasattr(chunk, 'chunk_id')]
        duplicate_ids = [cid for cid in set(chunk_ids) if chunk_ids.count(cid) > 1]
        if duplicate_ids:
            all_errors.append(f'Duplicate chunk IDs found: {duplicate_ids}')
            overall_score -= 10.0
        
        # Check chunk overlap and consistency
        overlap_analysis = ChunkValidator._analyze_chunk_overlap(chunks)
        if overlap_analysis['warnings']:
            all_warnings.extend(overlap_analysis['warnings'])
        
        return {
            'is_valid': len(all_errors) == 0,
            'errors': all_errors,
            'warnings': all_warnings,
            'overall_score': max(0.0, overall_score),
            'chunk_results': chunk_results,
            'overlap_analysis': overlap_analysis,
            'summary': {
                'total_chunks': len(chunks),
                'valid_chunks': sum(1 for r in chunk_results if r['result']['is_valid']),
                'invalid_chunks': sum(1 for r in chunk_results if not r['result']['is_valid']),
                'avg_chunk_length': sum(len(chunk.content) for chunk in chunks) / len(chunks) if chunks else 0
            }
        }
    
    @staticmethod
    def _check_content_quality(content: str) -> Dict[str, Any]:
        """Check the quality of chunk content."""
        warnings = []
        quality_metrics = {}
        
        if not content:
            return {'warnings': ['Empty content'], 'metrics': {}}
        
        # Check for excessive whitespace
        if re.search(r'\s{3,}', content):
            warnings.append('Excessive whitespace detected')
        
        # Check for repeated characters
        if re.search(r'(.)\1{4,}', content):
            warnings.append('Repeated characters detected')
        
        # Check for very long words (potential issues)
        words = content.split()
        long_words = [w for w in words if len(w) > 20]
        if long_words:
            warnings.append(f'Very long words detected: {len(long_words)} words > 20 chars')
        
        # Check for mixed case issues
        if content.isupper() and len(content) > 50:
            warnings.append('Content is all uppercase')
        
        # Calculate quality metrics
        quality_metrics['word_count'] = len(words)
        quality_metrics['avg_word_length'] = sum(len(w) for w in words) / max(len(words), 1)
        quality_metrics['whitespace_ratio'] = content.count(' ') / max(len(content), 1)
        quality_metrics['punctuation_ratio'] = len(re.findall(r'[.,!?;:]', content)) / max(len(content), 1)
        
        return {
            'warnings': warnings,
            'metrics': quality_metrics
        }
    
    @staticmethod
    def _analyze_chunk_overlap(chunks: List[Chunk]) -> Dict[str, Any]:
        """Analyze overlap and consistency between chunks."""
        warnings = []
        analysis = {}
        
        if len(chunks) < 2:
            return {'warnings': [], 'analysis': {'overlap_detected': False}}
        
        # Check for content overlap
        overlap_detected = False
        overlap_pairs = []
        
        for i in range(len(chunks) - 1):
            chunk1 = chunks[i].content
            chunk2 = chunks[i + 1].content
            
            # Simple overlap detection (can be enhanced)
            if len(chunk1) > 50 and len(chunk2) > 50:
                # Check for common substrings
                for length in range(20, min(len(chunk1), len(chunk2)) // 2):
                    for start in range(len(chunk1) - length + 1):
                        substring = chunk1[start:start + length]
                        if substring in chunk2:
                            overlap_pairs.append({
                                'chunk1_index': i,
                                'chunk2_index': i + 1,
                                'overlap_length': length,
                                'overlap_text': substring[:50] + '...' if len(substring) > 50 else substring
                            })
                            overlap_detected = True
                            break
                    if overlap_detected:
                        break
        
        if overlap_detected:
            warnings.append(f'Content overlap detected in {len(overlap_pairs)} chunk pairs')
        
        # Check chunk size consistency
        chunk_lengths = [len(chunk.content) for chunk in chunks]
        avg_length = sum(chunk_lengths) / len(chunk_lengths)
        length_variance = sum((l - avg_length) ** 2 for l in chunk_lengths) / len(chunk_lengths)
        
        if length_variance > avg_length * 2:
            warnings.append('High variance in chunk sizes detected')
        
        analysis = {
            'overlap_detected': overlap_detected,
            'overlap_pairs': overlap_pairs,
            'chunk_lengths': chunk_lengths,
            'avg_length': avg_length,
            'length_variance': length_variance,
            'size_consistency': 'good' if length_variance < avg_length else 'poor'
        }
        
        return {
            'warnings': warnings,
            'analysis': analysis
        }
    
    @staticmethod
    def get_chunk_statistics(chunks: List[Chunk]) -> Dict[str, Any]:
        """Get comprehensive statistics about chunks."""
        if not chunks:
            return {
                'total_chunks': 0,
                'total_content_length': 0,
                'avg_chunk_length': 0,
                'min_chunk_length': 0,
                'max_chunk_length': 0,
                'chunk_types': {},
                'metadata_keys': set()
            }
        
        content_lengths = [len(chunk.content) for chunk in chunks]
        chunk_types = {}
        metadata_keys = set()
        
        for chunk in chunks:
            # Count chunk types
            chunk_type = chunk.metadata.get('chunk_type', 'unknown') if chunk.metadata else 'unknown'
            chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
            
            # Collect metadata keys
            if chunk.metadata:
                metadata_keys.update(chunk.metadata.keys())
        
        return {
            'total_chunks': len(chunks),
            'total_content_length': sum(content_lengths),
            'avg_chunk_length': sum(content_lengths) / len(content_lengths),
            'min_chunk_length': min(content_lengths),
            'max_chunk_length': max(content_lengths),
            'chunk_types': chunk_types,
            'metadata_keys': list(metadata_keys),
            'length_distribution': {
                'short': len([l for l in content_lengths if l < 100]),
                'medium': len([l for l in content_lengths if 100 <= l < 500]),
                'long': len([l for l in content_lengths if l >= 500])
            }
        }
    
    @staticmethod
    def suggest_improvements(validation_result: Dict[str, Any]) -> List[str]:
        """Suggest improvements based on validation results."""
        suggestions = []
        
        if not validation_result['is_valid']:
            suggestions.append('Fix validation errors before proceeding')
        
        if validation_result['overall_score'] < 70:
            suggestions.append('Overall chunk quality is low - consider reviewing chunking strategy')
        
        # Analyze specific issues
        for chunk_result in validation_result['chunk_results']:
            if not chunk_result['result']['is_valid']:
                suggestions.append(f'Review chunk {chunk_result["chunk_id"]} for quality issues')
        
        # Check for common patterns
        if validation_result.get('overlap_analysis', {}).get('analysis', {}).get('overlap_detected'):
            suggestions.append('Consider reducing chunk overlap to avoid content duplication')
        
        if validation_result.get('summary', {}).get('avg_chunk_length', 0) > 1000:
            suggestions.append('Chunks are quite long - consider smaller chunk sizes for better retrieval')
        
        if validation_result.get('summary', {}).get('avg_chunk_length', 0) < 100:
            suggestions.append('Chunks are very short - consider larger chunk sizes for better context')
        
        return suggestions
