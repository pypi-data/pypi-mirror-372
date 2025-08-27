"""Structure-based chunking implementation."""

import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from .base import BaseChunker, Chunk
from ..exceptions import StructureParsingError


class StructureBasedChunker(BaseChunker):
    """Chunks text based on document structure (HTML, Markdown, etc.)."""
    
    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100,
                 preserve_structure: bool = True, **kwargs):
        """
        Initialize structure-based chunker.
        
        Args:
            max_chunk_size: Maximum chunk size in characters
            overlap: Number of overlapping characters
            preserve_structure: Whether to preserve structural elements
        """
        super().__init__(**kwargs)
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        self.preserve_structure = preserve_structure
    
    def chunk(self, text: str) -> List[Chunk]:
        """Chunk text based on document structure."""
        self._validate_input(text)
        
        # Detect document type and parse accordingly
        if self._is_html(text):
            return self._chunk_html(text)
        elif self._is_markdown(text):
            return self._chunk_markdown(text)
        else:
            # Fall back to paragraph-based chunking
            return self._chunk_plain_text(text)
    
    def _is_html(self, text: str) -> bool:
        """Check if text contains HTML tags."""
        html_pattern = r'<[^>]+>'
        return bool(re.search(html_pattern, text))
    
    def _is_markdown(self, text: str) -> bool:
        """Check if text contains Markdown elements."""
        markdown_patterns = [
            r'^#+\s',           # Headers
            r'^\*\s',           # Unordered lists
            r'^\d+\.\s',        # Ordered lists
            r'\*\*[^*]+\*\*',   # Bold text
            r'\*[^*]+\*',       # Italic text
            r'\[.*\]\(.*\)',     # Links
            r'`[^`]+`',         # Inline code
            r'```[\s\S]*```',   # Code blocks
        ]
        return any(re.search(pattern, text, re.MULTILINE) for pattern in markdown_patterns)
    
    def _chunk_html(self, text: str) -> List[Chunk]:
        """Chunk HTML text based on structural elements."""
        try:
            soup = BeautifulSoup(text, 'html.parser')
        except Exception as e:
            raise StructureParsingError(f"HTML parsing failed: {e}")
        
        # Extract text from different structural elements
        structural_elements = []
        
        # Process headers
        for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            structural_elements.append({
                'type': 'header',
                'level': int(header.name[1]),
                'text': header.get_text().strip(),
                'tag': header.name
            })
        
        # Process paragraphs
        for para in soup.find_all('p'):
            structural_elements.append({
                'type': 'paragraph',
                'text': para.get_text().strip(),
                'tag': 'p'
            })
        
        # Process lists
        for ul in soup.find_all(['ul', 'ol']):
            items = [li.get_text().strip() for li in ul.find_all('li')]
            structural_elements.append({
                'type': 'list',
                'text': '\n'.join(items),
                'tag': ul.name,
                'item_count': len(items)
            })
        
        # Process divs and other containers
        for div in soup.find_all('div'):
            text = div.get_text().strip()
            if text and len(text) > 50:  # Only include substantial divs
                structural_elements.append({
                    'type': 'container',
                    'text': text,
                    'tag': 'div'
                })
        
        return self._create_chunks_from_elements(structural_elements)
    
    def _chunk_markdown(self, text: str) -> List[Chunk]:
        """Chunk Markdown text based on structural elements."""
        lines = text.split('\n')
        structural_elements = []
        current_element = None
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_element:
                    structural_elements.append(current_element)
                    current_element = None
                continue
            
            # Check for headers
            header_match = re.match(r'^(#+)\s+(.+)$', line)
            if header_match:
                if current_element:
                    structural_elements.append(current_element)
                current_element = {
                    'type': 'header',
                    'level': len(header_match.group(1)),
                    'text': header_match.group(2),
                    'tag': f'h{len(header_match.group(1))}'
                }
                continue
            
            # Check for list items
            list_match = re.match(r'^(\*|\d+\.)\s+(.+)$', line)
            if list_match:
                if current_element and current_element['type'] == 'list':
                    current_element['text'] += '\n' + list_match.group(2)
                    current_element['item_count'] += 1
                else:
                    if current_element:
                        structural_elements.append(current_element)
                    current_element = {
                        'type': 'list',
                        'text': list_match.group(2),
                        'tag': 'ul' if list_match.group(1) == '*' else 'ol',
                        'item_count': 1
                    }
                continue
            
            # Regular paragraph content
            if current_element and current_element['type'] == 'paragraph':
                current_element['text'] += ' ' + line
            else:
                if current_element:
                    structural_elements.append(current_element)
                current_element = {
                    'type': 'paragraph',
                    'text': line,
                    'tag': 'p'
                }
        
        if current_element:
            structural_elements.append(current_element)
        
        return self._create_chunks_from_elements(structural_elements)
    
    def _chunk_plain_text(self, text: str) -> List[Chunk]:
        """Chunk plain text using paragraph boundaries."""
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if para:
                chunk = Chunk(
                    content=para,
                    chunk_id=self._get_next_id(),
                    metadata={
                        'chunk_type': 'structure_based',
                        'element_type': 'paragraph',
                        'paragraph_index': i
                    }
                )
                chunks.append(chunk)
        
        return chunks
    
    def _create_chunks_from_elements(self, elements: List[Dict[str, Any]]) -> List[Chunk]:
        """Create chunks from structural elements."""
        chunks = []
        current_chunk = []
        current_size = 0
        
        for element in elements:
            element_text = element['text']
            element_size = len(element_text)
            
            if current_size + element_size > self.max_chunk_size and current_chunk:
                # Create chunk from current elements
                chunk_content = '\n\n'.join([elem['text'] for elem in current_chunk])
                chunk = Chunk(
                    content=chunk_content,
                    chunk_id=self._get_next_id(),
                    metadata={
                        'chunk_type': 'structure_based',
                        'element_count': len(current_chunk),
                        'element_types': [elem['type'] for elem in current_chunk],
                        'preserve_structure': self.preserve_structure
                    }
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_elements = current_chunk[-1:] if self.overlap > 0 else []
                current_chunk = overlap_elements
                current_size = sum(len(elem['text']) for elem in overlap_elements)
            
            current_chunk.append(element)
            current_size += element_size
        
        # Create final chunk
        if current_chunk:
            chunk_content = '\n\n'.join([elem['text'] for elem in current_chunk])
            chunk = Chunk(
                content=chunk_content,
                chunk_id=self._get_next_id(),
                metadata={
                    'chunk_type': 'structure_based',
                    'element_count': len(current_chunk),
                    'element_types': [elem['type'] for elem in current_chunk],
                    'preserve_structure': self.preserve_structure
                }
            )
            chunks.append(chunk)
        
        return chunks

