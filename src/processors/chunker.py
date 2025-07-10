"""Text chunking functionality."""

from typing import List, Dict, Any

from ..models.core import BookChunk
from ..utils import count_words, split_into_sentences


class TextChunker:
    """Chunks text into reading sessions."""
    
    def __init__(self, target_reading_time: float = 10.0, words_per_minute: int = 200):
        """Initialize text chunker."""
        self.target_reading_time = target_reading_time
        self.words_per_minute = words_per_minute
    
    def chunk_text(self, text: str) -> List[BookChunk]:
        """Chunk text into reading sessions while preserving paragraph structure."""
        if not text.strip():
            return []
        
        target_words = int(self.target_reading_time * self.words_per_minute)
        
        # Split into paragraphs first to preserve structure
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk_paragraphs = []
        current_word_count = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            paragraph_words = count_words(paragraph)
            
            # If adding this paragraph would exceed target and we have content, create chunk
            if current_word_count + paragraph_words > target_words and current_chunk_paragraphs:
                # Create chunk from current paragraphs
                chunk_text = '\n\n'.join(current_chunk_paragraphs)
                chunks.append(self._create_chunk(len(chunks), chunk_text))
                
                # Start new chunk with this paragraph
                current_chunk_paragraphs = [paragraph]
                current_word_count = paragraph_words
            else:
                # Add paragraph to current chunk
                current_chunk_paragraphs.append(paragraph)
                current_word_count += paragraph_words
        
        # Create final chunk if we have content
        if current_chunk_paragraphs:
            chunk_text = '\n\n'.join(current_chunk_paragraphs)
            chunks.append(self._create_chunk(len(chunks), chunk_text))
        
        return chunks
    
    def _create_chunk(self, index: int, content: str) -> BookChunk:
        """Create a BookChunk object."""
        word_count = count_words(content)
        reading_time = word_count / self.words_per_minute
        
        return BookChunk(
            index=index,
            content=content,
            word_count=word_count,
            estimated_reading_time=reading_time
        )
    
    def chunk_to_dict(self, chunks: List[BookChunk]) -> List[Dict[str, Any]]:
        """Convert chunks to dictionary format for JSON storage."""
        return [
            {
                "index": chunk.index,
                "content": chunk.content,
                "word_count": chunk.word_count,
                "estimated_reading_time": chunk.estimated_reading_time
            }
            for chunk in chunks
        ]