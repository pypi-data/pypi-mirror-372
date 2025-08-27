"""Text processing utilities for chunking operations."""

import re
import unicodedata
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup


class TextProcessor:
    """Utility class for text processing operations."""
    
    @staticmethod
    def clean_text(text: str, remove_html: bool = True, normalize_whitespace: bool = True,
                   remove_special_chars: bool = False) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Input text to clean
            remove_html: Whether to remove HTML tags
            normalize_whitespace: Whether to normalize whitespace
            remove_special_chars: Whether to remove special characters
            
        Returns:
            Cleaned text
        """
        if not text:
            return text
        
        # Remove HTML tags
        if remove_html:
            text = TextProcessor.remove_html_tags(text)
        
        # Normalize unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Normalize whitespace
        if normalize_whitespace:
            text = TextProcessor.normalize_whitespace(text)
        
        # Remove special characters
        if remove_special_chars:
            text = TextProcessor.remove_special_characters(text)
        
        return text.strip()
    
    @staticmethod
    def remove_html_tags(text: str) -> str:
        """Remove HTML tags from text."""
        if not text:
            return text
        
        try:
            soup = BeautifulSoup(text, 'html.parser')
            return soup.get_text()
        except Exception:
            # Fallback to regex if BeautifulSoup fails
            return re.sub(r'<[^>]+>', '', text)
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text."""
        if not text:
            return text
        
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        # Normalize line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    @staticmethod
    def remove_special_characters(text: str, keep_punctuation: bool = True) -> str:
        """Remove special characters from text."""
        if not text:
            return text
        
        if keep_punctuation:
            # Keep basic punctuation and alphanumeric
            pattern = r'[^\w\s.,!?;:()"\'-]'
        else:
            # Keep only alphanumeric and spaces
            pattern = r'[^\w\s]'
        
        return re.sub(pattern, '', text)
    
    @staticmethod
    def extract_sentences(text: str, language: str = 'english') -> List[str]:
        """Extract sentences from text."""
        if not text:
            return []
        
        # Simple sentence splitting (can be enhanced with NLTK)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    @staticmethod
    def extract_paragraphs(text: str) -> List[str]:
        """Extract paragraphs from text."""
        if not text:
            return []
        
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        return paragraphs
    
    @staticmethod
    def extract_words(text: str, min_length: int = 1) -> List[str]:
        """Extract words from text."""
        if not text:
            return []
        
        words = re.findall(r'\b\w+\b', text.lower())
        words = [w for w in words if len(w) >= min_length]
        return words
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text."""
        return len(TextProcessor.extract_words(text))
    
    @staticmethod
    def count_characters(text: str, include_spaces: bool = True) -> int:
        """Count characters in text."""
        if not text:
            return 0
        
        if include_spaces:
            return len(text)
        else:
            return len(text.replace(' ', ''))
    
    @staticmethod
    def get_text_statistics(text: str) -> Dict[str, Any]:
        """Get comprehensive text statistics."""
        if not text:
            return {
                'characters': 0,
                'characters_no_spaces': 0,
                'words': 0,
                'sentences': 0,
                'paragraphs': 0,
                'avg_word_length': 0.0,
                'avg_sentence_length': 0.0,
                'avg_paragraph_length': 0.0
            }
        
        words = TextProcessor.extract_words(text)
        sentences = TextProcessor.extract_sentences(text)
        paragraphs = TextProcessor.extract_paragraphs(text)
        
        char_count = len(text)
        char_count_no_spaces = len(text.replace(' ', ''))
        word_count = len(words)
        sentence_count = len(sentences)
        paragraph_count = len(paragraphs)
        
        avg_word_length = sum(len(w) for w in words) / max(word_count, 1)
        avg_sentence_length = word_count / max(sentence_count, 1)
        avg_paragraph_length = word_count / max(paragraph_count, 1)
        
        return {
            'characters': char_count,
            'characters_no_spaces': char_count_no_spaces,
            'words': word_count,
            'sentences': sentence_count,
            'paragraphs': paragraph_count,
            'avg_word_length': round(avg_word_length, 2),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_paragraph_length': round(avg_paragraph_length, 2)
        }
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Simple language detection based on common words."""
        if not text:
            return 'unknown'
        
        # Simple heuristics for common languages
        text_lower = text.lower()
        
        # English common words
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        english_count = sum(1 for word in english_words if word in text_lower)
        
        # Spanish common words
        spanish_words = ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te']
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        
        # French common words
        french_words = ['le', 'la', 'de', 'et', 'à', 'en', 'un', 'est', 'se', 'ne', 'pas', 'vous']
        french_count = sum(1 for word in french_words if word in text_lower)
        
        # German common words
        german_words = ['der', 'die', 'das', 'und', 'in', 'den', 'von', 'zu', 'mit', 'sich', 'auf', 'für']
        german_count = sum(1 for word in german_words if word in text_lower)
        
        # Find the language with most matches
        language_scores = {
            'english': english_count,
            'spanish': spanish_count,
            'french': french_count,
            'german': german_count
        }
        
        max_score = max(language_scores.values())
        if max_score > 0:
            return max(language_scores, key=language_scores.get)
        
        return 'unknown'
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10, min_length: int = 3) -> List[str]:
        """Extract potential keywords from text."""
        if not text:
            return []
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        words = TextProcessor.extract_words(text, min_length)
        words = [w for w in words if w not in stop_words and len(w) >= min_length]
        
        # Count word frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:max_keywords]]
        
        return keywords
    
    @staticmethod
    def split_text_into_chunks(text: str, chunk_size: int, overlap: int = 0) -> List[str]:
        """Split text into chunks with optional overlap."""
        if not text or chunk_size <= 0:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk)
            
            # Move start position (accounting for overlap)
            start = max(end - overlap, start + 1)
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks
