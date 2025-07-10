"""EPUB file processing functionality."""

import zipfile
import re
from pathlib import Path
from typing import List, Optional
from xml.etree import ElementTree as ET


class EpubProcessor:
    """Processes EPUB files to extract readable text."""
    
    def __init__(self):
        """Initialize EPUB processor."""
        self.html_tag_pattern = re.compile(r'<[^>]+>')
        self.whitespace_pattern = re.compile(r'\s+')
    
    def extract_text(self, epub_path: Path) -> str:
        """Extract text content from EPUB file."""
        try:
            with zipfile.ZipFile(epub_path, 'r') as epub_zip:
                # Get content files in reading order
                content_files = self._get_content_files(epub_zip)
                
                # Extract text from each content file
                text_parts = []
                for content_file in content_files:
                    try:
                        content = epub_zip.read(content_file).decode('utf-8')
                        text = self._extract_text_from_html(content)
                        if text.strip():
                            text_parts.append(text)
                    except Exception as e:
                        # Skip files that can't be processed
                        continue
                
                # Combine all text parts
                return '\n\n'.join(text_parts)
        
        except Exception as e:
            raise Exception(f"Failed to process EPUB file: {e}")
    
    def _get_content_files(self, epub_zip: zipfile.ZipFile) -> List[str]:
        """Get list of content files in reading order."""
        # For now, use a simple approach: get all HTML files and sort them
        # A more sophisticated approach would parse the OPF file to get the spine order
        content_files = []
        
        for file_info in epub_zip.filelist:
            filename = file_info.filename
            if filename.endswith(('.html', '.xhtml', '.htm')):
                # Skip common non-content files
                if not any(skip in filename.lower() for skip in ['toc', 'cover', 'copyright', 'style']):
                    content_files.append(filename)
        
        # Sort files to get a reasonable reading order
        # Chapter files often have 'chap' in the name
        def sort_key(filename):
            # Prioritize chapter files
            if 'chap' in filename.lower():
                return (0, filename)
            # Then other content files
            return (1, filename)
        
        content_files.sort(key=sort_key)
        return content_files
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract text from HTML content while preserving structure."""
        # First, handle common HTML structures before stripping tags
        text = html_content
        
        # Convert headings to formatted text with proper spacing
        for i in range(1, 7):  # h1 through h6
            text = re.sub(f'<h{i}[^>]*>', '\n\n## ', text, flags=re.IGNORECASE)
            text = re.sub(f'</h{i}>', '\n\n', text, flags=re.IGNORECASE)
        
        # Convert paragraphs to proper line breaks
        text = re.sub(r'<p[^>]*>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
        
        # Convert div elements to paragraph breaks
        text = re.sub(r'<div[^>]*>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</div>', '\n\n', text, flags=re.IGNORECASE)
        
        # Convert line breaks
        text = re.sub(r'<br[^>]*/?>', '\n', text, flags=re.IGNORECASE)
        
        # Handle emphasis (keep some basic formatting cues)
        text = re.sub(r'<em[^>]*>', '*', text, flags=re.IGNORECASE)
        text = re.sub(r'</em>', '*', text, flags=re.IGNORECASE)
        text = re.sub(r'<i[^>]*>', '*', text, flags=re.IGNORECASE)
        text = re.sub(r'</i>', '*', text, flags=re.IGNORECASE)
        
        text = re.sub(r'<strong[^>]*>', '**', text, flags=re.IGNORECASE)
        text = re.sub(r'</strong>', '**', text, flags=re.IGNORECASE)
        text = re.sub(r'<b[^>]*>', '**', text, flags=re.IGNORECASE)
        text = re.sub(r'</b>', '**', text, flags=re.IGNORECASE)
        
        # Remove all other HTML tags
        text = self.html_tag_pattern.sub('', text)
        
        # Decode HTML entities
        text = self._decode_html_entities(text)
        
        # Clean up excessive whitespace while preserving paragraph structure
        text = self._clean_whitespace(text)
        
        return text.strip()
    
    def _decode_html_entities(self, text: str) -> str:
        """Decode common HTML entities."""
        entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&nbsp;': ' ',
            '&mdash;': '—',
            '&ndash;': '–',
            '&ldquo;': '"',
            '&rdquo;': '"',
            '&lsquo;': ''',
            '&rsquo;': ''',
            '&hellip;': '…'
        }
        
        for entity, replacement in entities.items():
            text = text.replace(entity, replacement)
        
        return text
    
    def _clean_whitespace(self, text: str) -> str:
        """Clean whitespace while preserving paragraph structure."""
        # Split into lines and process each
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Clean up spaces and tabs within each line
            cleaned_line = re.sub(r'[ \t]+', ' ', line.strip())
            cleaned_lines.append(cleaned_line)
        
        # Join lines back together
        text = '\n'.join(cleaned_lines)
        
        # Reduce multiple consecutive newlines to double newlines (paragraph breaks)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def _get_spine_order(self, epub_zip: zipfile.ZipFile) -> List[str]:
        """Get content files in spine order from OPF file (more sophisticated approach)."""
        # This is a more complex implementation that could be added later
        # It would parse the OPF file to get the proper reading order
        pass