"""Core data models."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Settings:
    """Application settings."""
    user_email: str = "user@example.com"
    user_name: str = "Reader"
    target_reading_time_minutes: int = 10
    words_per_minute: int = 200
    current_book: str = ""
    book_storage_path: str = "data/books"
    
    # Email settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = ""
    sender_password: str = ""
    enable_email: bool = False


@dataclass
class BookProgress:
    """Progress tracking for a book."""
    current_chunk: int = 0
    total_chunks: int = 0
    reading_days: int = 0
    completed: bool = False
    
    @property
    def progress_percentage(self) -> float:
        """Calculate reading progress as percentage."""
        if self.total_chunks == 0:
            return 0.0
        return (self.current_chunk / self.total_chunks) * 100
    
    def mark_chunk_read(self) -> None:
        """Mark current chunk as read and advance to next."""
        if self.current_chunk < self.total_chunks:
            self.current_chunk += 1
            self.reading_days += 1
            
            if self.current_chunk >= self.total_chunks:
                self.completed = True
    
    def is_finished(self) -> bool:
        """Check if book reading is finished."""
        return self.completed or self.current_chunk >= self.total_chunks


@dataclass
class BookChunk:
    """A chunk of text from a book."""
    index: int
    content: str
    word_count: int
    estimated_reading_time: float