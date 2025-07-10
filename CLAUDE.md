# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Setup and Basic Operations
```bash
# Initial setup
python -m src.main setup

# Process a book into chunks
python -m src.main process data/books/book.txt

# Read daily portion (preview)
python -m src.main read book.txt

# Read and mark progress
python -m src.main read book.txt --send

# Check status
python -m src.main status

# Test email configuration
python -m src.main test-email
```

### Development Commands
```bash
# Run the application
python -m src.main

# Test with sample book (text file)
python -m src.main process data/books/test_book.txt
python -m src.main read test_book.txt --send

# Test with EPUB file
python -m src.main process data/books/book.epub
python -m src.main read book.epub --send
```

## Architecture Overview

The Daily Reading Companion is a Python-based CLI tool that chunks books into daily reading portions. It follows a modular architecture with clear separation of concerns:

### Core Components
- **Main CLI** (`src/main.py`) - Entry point with command handling
- **Models** (`src/models/core.py`) - Data structures (Settings, BookProgress, BookChunk)
- **Services** - Business logic layer
  - `ConfigService` - Configuration management with env overrides
  - `ProgressService` - Reading progress tracking
  - `EmailService` - Gmail SMTP email delivery
- **Processors** - Content extraction and text chunking
  - `TextChunker` - Chunks text based on reading time
  - `EpubProcessor` - Extracts text from EPUB files
- **Utils** (`src/utils.py`) - Text processing and file operations

### Data Flow
1. Books (text files or EPUB) are processed into chunks based on target reading time
2. EPUB files are extracted to plain text, then processed like text files
3. Chunks stored as JSON with metadata (word count, reading time)
4. Progress tracked per book with completion status
5. Daily reading delivered via CLI with progress updates

### Key Design Patterns
- **Zero dependencies** - Pure Python implementation
- **Dataclass models** - Type-safe data structures
- **Service layer** - Business logic abstraction
- **Configuration flexibility** - File + environment variable overrides
- **Stateful progress** - JSON-based persistence

### Configuration System
- Settings stored in `data/settings.json`
- Environment variable overrides:
  - `DAILY_READER_EMAIL` - User email
  - `DAILY_READER_READING_TIME` - Reading time in minutes
  - `DAILY_READER_SENDER_EMAIL` - Gmail sender address
  - `DAILY_READER_SENDER_PASSWORD` - Gmail app-specific password
  - `DAILY_READER_ENABLE_EMAIL` - Enable email delivery (true/false)
- Default values defined in `Settings` dataclass

### Email Setup (Gmail)
1. Enable 2-factor authentication on Gmail account
2. Generate app-specific password in Gmail settings
3. Configure `data/settings.json`:
   ```json
   {
     "user_email": "recipient@gmail.com",
     "sender_email": "sender@gmail.com", 
     "sender_password": "app-specific-password",
     "enable_email": true
   }
   ```
4. Test with `python -m src.main test-email`

### Text Processing
- **File Format Support**: Plain text files (.txt) and EPUB files (.epub)
- **EPUB Processing**: Extracts text from HTML/XHTML files within EPUB archives
- **Sentence-based chunking** for natural breaks
- **Word count estimation** for reading time
- **Text cleaning and normalization**
- **Multiple encoding support** (UTF-8, Latin-1 fallback)

### Progress Tracking
- Per-book progress with chunk indexing
- Reading days counter
- Completion status
- Statistics aggregation across books

## Development Notes

### Code Style
- Uses dataclasses for models
- Type hints throughout
- Minimal dependencies philosophy
- Clear separation between CLI and business logic

### Testing Strategy
- Test books available in `data/books/`
- Progress data in `data/progress.json`
- Chunk data stored as `{book_stem}_chunks.json`

### GitHub Actions Deployment
- Workflow file: `.github/workflows/daily-reading.yml`
- Runs daily at 9:00 AM UTC (configurable)
- Uses environment variables from GitHub Secrets
- Automatically commits progress updates
- Finds active books and sends next reading portion

### Secrets Configuration (GitHub Settings → Secrets)
- `DAILY_READER_EMAIL` - Recipient email
- `DAILY_READER_SENDER_EMAIL` - Gmail sender  
- `DAILY_READER_SENDER_PASSWORD` - Gmail app password
- `DAILY_READER_READING_TIME` - Minutes per session (optional)

### Extension Points
- **New processors** can be added for different formats (PDF, MOBI, etc.)
- **Service layer** supports additional delivery methods
- **Configuration system** easily extensible
- **Progress tracking** can support additional metrics
- **EPUB processor** can be enhanced to parse OPF files for proper chapter ordering