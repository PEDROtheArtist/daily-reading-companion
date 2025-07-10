"""Simple configuration service."""

import os
from pathlib import Path

from ..models.core import Settings
from ..utils import load_json, ensure_directory


class ConfigService:
    """Simple configuration service."""
    
    def __init__(self, data_dir: Path = None):
        """Initialize configuration service."""
        self.data_dir = data_dir or Path("data")
        ensure_directory(self.data_dir)
        self.settings_file = self.data_dir / "settings.json"
    
    def load_settings(self) -> Settings:
        """Load configuration settings."""
        # Load from file if it exists
        config = {}
        if self.settings_file.exists():
            config = load_json(self.settings_file)
        
        # Apply environment overrides
        if os.getenv("DAILY_READER_EMAIL"):
            config["user_email"] = os.getenv("DAILY_READER_EMAIL")
        
        if os.getenv("DAILY_READER_READING_TIME"):
            try:
                config["target_reading_time_minutes"] = int(os.getenv("DAILY_READER_READING_TIME"))
            except ValueError:
                pass
        
        # Email environment overrides
        if os.getenv("DAILY_READER_SENDER_EMAIL"):
            config["sender_email"] = os.getenv("DAILY_READER_SENDER_EMAIL")
        
        if os.getenv("DAILY_READER_SENDER_PASSWORD"):
            config["sender_password"] = os.getenv("DAILY_READER_SENDER_PASSWORD")
        
        if os.getenv("DAILY_READER_ENABLE_EMAIL"):
            config["enable_email"] = os.getenv("DAILY_READER_ENABLE_EMAIL").lower() == "true"
        
        return Settings(**config)
    
    def save_settings(self, settings: Settings) -> None:
        """Save settings to file."""
        from ..utils import save_json
        save_json(self.settings_file, {
            "user_email": settings.user_email,
            "user_name": settings.user_name,
            "target_reading_time_minutes": settings.target_reading_time_minutes,
            "words_per_minute": settings.words_per_minute,
            "current_book": settings.current_book,
            "book_storage_path": settings.book_storage_path,
            "smtp_server": settings.smtp_server,
            "smtp_port": settings.smtp_port,
            "sender_email": settings.sender_email,
            "sender_password": settings.sender_password,
            "enable_email": settings.enable_email
        })