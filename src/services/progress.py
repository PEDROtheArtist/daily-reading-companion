"""Simple progress tracking service."""

from pathlib import Path
from typing import Dict, Any

from ..models.core import BookProgress
from ..utils import load_json, save_json, ensure_directory


class ProgressService:
    """Service for tracking reading progress."""
    
    def __init__(self, data_dir: Path = None):
        """Initialize progress service."""
        self.data_dir = data_dir or Path("data")
        ensure_directory(self.data_dir)
        self.progress_file = self.data_dir / "progress.json"
    
    def load_progress(self) -> Dict[str, Any]:
        """Load progress data."""
        if self.progress_file.exists():
            return load_json(self.progress_file)
        return {"books": {}}
    
    def save_progress(self, progress_data: Dict[str, Any]):
        """Save progress data."""
        save_json(self.progress_file, progress_data)
    
    def get_book_progress(self, book_filename: str) -> BookProgress:
        """Get progress for a book."""
        progress_data = self.load_progress()
        book_data = progress_data["books"].get(book_filename, {})
        
        return BookProgress(
            current_chunk=book_data.get("current_chunk", 0),
            total_chunks=book_data.get("total_chunks", 0),
            reading_days=book_data.get("reading_days", 0),
            completed=book_data.get("completed", False)
        )
    
    def update_book_progress(self, book_filename: str, total_chunks: int) -> BookProgress:
        """Update progress for a book."""
        progress_data = self.load_progress()
        
        if "books" not in progress_data:
            progress_data["books"] = {}
        
        if book_filename not in progress_data["books"]:
            progress_data["books"][book_filename] = {}
        
        book_progress = self.get_book_progress(book_filename)
        book_progress.total_chunks = total_chunks
        book_progress.mark_chunk_read()
        
        # Save updated progress
        progress_data["books"][book_filename] = {
            "current_chunk": book_progress.current_chunk,
            "total_chunks": book_progress.total_chunks,
            "reading_days": book_progress.reading_days,
            "completed": book_progress.completed
        }
        
        self.save_progress(progress_data)
        return book_progress
    
    def set_book_total_chunks(self, book_filename: str, total_chunks: int):
        """Set total chunks for a book."""
        progress_data = self.load_progress()
        
        if "books" not in progress_data:
            progress_data["books"] = {}
        
        if book_filename not in progress_data["books"]:
            progress_data["books"][book_filename] = {}
        
        progress_data["books"][book_filename]["total_chunks"] = total_chunks
        self.save_progress(progress_data)
    
    def get_reading_statistics(self) -> Dict[str, Any]:
        """Get reading statistics."""
        progress_data = self.load_progress()
        
        active_books = 0
        completed_books = 0
        total_reading_days = 0
        
        for book_data in progress_data.get("books", {}).values():
            if book_data.get("completed", False):
                completed_books += 1
            else:
                active_books += 1
            total_reading_days += book_data.get("reading_days", 0)
        
        return {
            "active_books": active_books,
            "completed_books": completed_books,
            "total_reading_days": total_reading_days
        }