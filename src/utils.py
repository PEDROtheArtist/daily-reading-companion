"""Essential utilities for Daily Reading Companion."""

import json
import re
from pathlib import Path
from typing import List, Dict, Any


# Text utilities
def count_words(text: str) -> int:
    """Count words in text."""
    if not text.strip():
        return 0
    words = [word for word in text.split() if word.strip()]
    return len(words)


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace while preserving paragraph structure."""
    if not text:
        return ""
    
    # Split into lines to preserve newlines
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Clean up spaces and tabs within each line
        line = re.sub(r'[ \t]+', ' ', line.strip())
        cleaned_lines.append(line)
    
    # Join lines back together
    text = '\n'.join(cleaned_lines)
    
    # Normalize quotes
    text = re.sub(r'["""]', '"', text)
    text = re.sub(r"[''']", "'", text)
    
    # Clean up excessive newlines (max 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    if not text.strip():
        return []
    text = re.sub(r'([.!?])\s+([A-Z])', r'\1\n\2', text)
    sentences = text.split('\n')
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


# File utilities
def ensure_directory(path: Path) -> None:
    """Ensure directory exists, creating if necessary."""
    path.mkdir(parents=True, exist_ok=True)


def load_json(file_path: Path) -> Dict[str, Any]:
    """Load JSON data from file."""
    if not file_path.exists():
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(file_path: Path, data: Dict[str, Any]) -> None:
    """Save JSON data to file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)