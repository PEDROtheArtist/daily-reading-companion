# Daily Reading Companion

A minimal system for breaking books into daily reading chunks. Zero dependencies, pure Python.

## Core Functionality

- Process text files into time-based reading chunks
- Track reading progress automatically
- Simple CLI interface for daily use

## Usage

```bash
# Setup
python -m src.main setup

# Process a book
python -m src.main process data/books/book.txt

# Read daily chunk (preview)
python -m src.main read book.txt

# Read and mark as complete
python -m src.main read book.txt --send

# Check status
python -m src.main status
```

## Configuration

Edit `data/settings.json`:
```json
{
  "user_email": "your@email.com",
  "target_reading_time_minutes": 10,
  "words_per_minute": 200
}
```

## Architecture

```
src/
├── main.py              # CLI interface
├── utils.py             # Text/file utilities
├── models/core.py       # Data models
├── services/            # Config & progress
└── processors/chunker.py # Text chunking
```

## Data Files

- `data/books/` - Your text files
- `data/progress.json` - Reading progress
- `data/settings.json` - Configuration

## Requirements

- Python 3.9+
- No external dependencies

## GitHub Actions Deployment

For automated daily delivery, deploy to GitHub with Actions:

1. **Set up repository secrets** (see `github-setup.md`)
2. **Push your books and progress** to the repository  
3. **Configure schedule** in `.github/workflows/daily-reading.yml`
4. **Workflow runs daily** and emails your reading portion

The system automatically commits progress updates back to the repository.

## Development

The system is designed for easy extension:

- ✅ EPUB support implemented
- ✅ Email delivery via Gmail implemented  
- ✅ GitHub Actions automation ready
- Add web interface as separate module

Current implementation is production-ready for text files and EPUB books.# daily-reading-companion
