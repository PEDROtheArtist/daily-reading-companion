#!/usr/bin/env python3
"""Main CLI for Daily Reading Companion."""

import sys
import json
from pathlib import Path
from typing import Optional

from .services.config import ConfigService
from .services.progress import ProgressService
from .services.email import EmailService
from .processors.chunker import TextChunker
from .processors.epub import EpubProcessor
from .utils import count_words, clean_text, save_json, load_json, ensure_directory


def setup_command():
    """Set up the system."""
    print("🔧 Setting up Daily Reading Companion...")
    
    # Create directories
    for dir_name in ['data/books', 'data/backups', 'logs']:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    print("✅ Directories created")
    
    # Load configuration
    config_service = ConfigService()
    settings = config_service.load_settings()
    print("✅ Configuration loaded")
    print(f"   User: {settings.user_email}")
    print(f"   Reading time: {settings.target_reading_time_minutes} minutes")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit data/settings.json to configure your email")
    print("2. Add a text file to data/books/")
    print("3. Run 'python -m src.main process <filename>'")
    print("4. Run 'python -m src.main read <filename>'")


def process_book_command(file_path: str):
    """Process a text file into chunks."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"📚 Processing: {path.name}")
    
    # Determine file type and extract content
    file_extension = path.suffix.lower()
    
    try:
        if file_extension == '.epub':
            print("📖 Detected EPUB file, extracting text...")
            epub_processor = EpubProcessor()
            content = epub_processor.extract_text(path)
        else:
            # Handle as text file
            print("📄 Processing as text file...")
            try:
                content = path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                content = path.read_text(encoding='latin1')
    except Exception as e:
        print(f"❌ Could not process file: {e}")
        return
    
    # Clean content
    content = clean_text(content)
    word_count = count_words(content)
    
    print(f"✅ Loaded: {word_count} words")
    
    # Load settings
    config_service = ConfigService()
    settings = config_service.load_settings()
    
    # Chunk text
    print("✂️  Creating chunks...")
    chunker = TextChunker(
        target_reading_time=settings.target_reading_time_minutes,
        words_per_minute=settings.words_per_minute
    )
    
    chunks = chunker.chunk_text(content)
    
    print(f"✅ Created {len(chunks)} chunks")
    
    # Calculate reading time
    total_time = sum(chunk.estimated_reading_time for chunk in chunks)
    avg_time = total_time / len(chunks) if chunks else 0
    
    print(f"   Total reading time: {total_time:.1f} minutes")
    print(f"   Average chunk time: {avg_time:.1f} minutes")
    
    # Save chunk data
    chunk_data = {
        "title": path.stem,
        "chunks": chunker.chunk_to_dict(chunks),
        "total_chunks": len(chunks),
        "total_words": word_count,
        "total_reading_time": total_time
    }
    
    chunk_file = Path("data") / f"{path.stem}_chunks.json"
    save_json(chunk_file, chunk_data)
    print(f"✅ Saved chunks to: {chunk_file}")
    
    # Update progress
    progress_service = ProgressService()
    progress_service.set_book_total_chunks(path.name, len(chunks))
    
    print("🎉 Book processed successfully!")


def read_daily_command(book_filename: str = None, send: bool = False):
    """Read daily portion."""
    config_service = ConfigService()
    settings = config_service.load_settings()
    
    if not book_filename:
        book_filename = settings.current_book
    
    if not book_filename:
        print("❌ No book specified. Use: python -m src.main read <filename>")
        return
    
    # Load chunk data
    stem = Path(book_filename).stem
    chunk_file = Path("data") / f"{stem}_chunks.json"
    
    if not chunk_file.exists():
        print(f"❌ No chunks found for {book_filename}. Process the book first:")
        print(f"   python -m src.main process data/books/{book_filename}")
        return
    
    chunk_data = load_json(chunk_file)
    
    # Get progress
    progress_service = ProgressService()
    progress = progress_service.get_book_progress(book_filename)
    
    if progress.current_chunk >= len(chunk_data['chunks']):
        print("🎉 Book completed!")
        return
    
    chunk = chunk_data['chunks'][progress.current_chunk]
    progress_pct = ((progress.current_chunk + 1) / len(chunk_data['chunks'])) * 100
    is_final = progress.current_chunk + 1 >= len(chunk_data['chunks'])
    
    print(f"\n📖 Daily Reading: {chunk_data['title']}")
    print("=" * 50)
    print(f"Day: {progress.reading_days + 1}")
    print(f"Progress: {progress.current_chunk + 1}/{len(chunk_data['chunks'])} ({progress_pct:.1f}%)")
    print(f"Reading time: {chunk['estimated_reading_time']:.1f} minutes")
    print(f"Words: {chunk['word_count']}")
    print()
    print("Content:")
    print("-" * 30)
    
    # Show content with nice formatting
    content = chunk['content']
    if len(content) > 500:
        # Show first part for preview
        print(content[:500] + "...")
        print(f"\n[{len(content) - 500} more characters...]")
    else:
        print(content)
    
    print("-" * 30)
    
    if send:
        # Update progress
        progress_service.update_book_progress(book_filename, len(chunk_data['chunks']))
        print("\n✅ Progress updated!")
        
        # Send email if enabled
        if settings.enable_email:
            email_service = EmailService(settings)
            email_progress = {
                'day': progress.reading_days + 1,
                'current_chunk': progress.current_chunk + 1,
                'total_chunks': len(chunk_data['chunks'])
            }
            email_service.send_daily_chunk(chunk_data['title'], chunk, email_progress)
        
        if is_final:
            print("🎉 Congratulations! You've completed the book!")
    else:
        print("\n📋 This was a preview. Use --send to update progress:")
        print(f"   python -m src.main read {book_filename} --send")


def status_command():
    """Show status."""
    config_service = ConfigService()
    progress_service = ProgressService()
    
    settings = config_service.load_settings()
    stats = progress_service.get_reading_statistics()
    
    print("📊 Daily Reading Status")
    print("=" * 30)
    print(f"User: {settings.user_email}")
    print(f"Reading time: {settings.target_reading_time_minutes} minutes")
    
    print(f"\nStatistics:")
    print(f"Active books: {stats['active_books']}")
    print(f"Completed books: {stats['completed_books']}")
    print(f"Total reading days: {stats['total_reading_days']}")
    
    # Show available books
    books_dir = Path(settings.book_storage_path)
    if books_dir.exists():
        book_files = list(books_dir.glob("*.txt"))
        if book_files:
            print(f"\nAvailable books:")
            for book_file in book_files:
                progress = progress_service.get_book_progress(book_file.name)
                if progress.total_chunks > 0:
                    pct = progress.progress_percentage
                    status_text = "✅ Completed" if progress.completed else f"📖 Reading ({pct:.0f}%)"
                    print(f"  {book_file.name}: {status_text}")
                else:
                    print(f"  {book_file.name}: ⚠️  Not processed")


def test_email_command():
    """Test email configuration."""
    config_service = ConfigService()
    settings = config_service.load_settings()
    
    print("📧 Testing email configuration...")
    print(f"SMTP Server: {settings.smtp_server}:{settings.smtp_port}")
    print(f"Sender Email: {settings.sender_email}")
    print(f"Recipient Email: {settings.user_email}")
    print(f"Email Enabled: {settings.enable_email}")
    
    if not settings.enable_email:
        print("❌ Email is disabled. Enable it in settings to test.")
        return
    
    email_service = EmailService(settings)
    success = email_service.test_email_connection()
    
    if success:
        print("✅ Email configuration is working!")
    else:
        print("❌ Email configuration needs to be fixed.")
        print("\nSetup instructions:")
        print("1. Enable 2-factor authentication on your Gmail account")
        print("2. Generate an app-specific password")
        print("3. Update your settings.json with:")
        print("   - sender_email: your Gmail address")
        print("   - sender_password: your app-specific password")
        print("   - enable_email: true")


def main():
    """Main CLI."""
    if len(sys.argv) < 2:
        print("Daily Reading Companion")
        print()
        print("Usage:")
        print("  python -m src.main setup")
        print("  python -m src.main process <file.txt>")
        print("  python -m src.main read [filename] [--send]")
        print("  python -m src.main status")
        print("  python -m src.main test-email")
        print()
        print("Examples:")
        print("  python -m src.main setup")
        print("  python -m src.main process data/books/my_book.txt")
        print("  python -m src.main read my_book.txt")
        print("  python -m src.main read my_book.txt --send")
        print("  python -m src.main test-email")
        return
    
    command = sys.argv[1]
    
    try:
        if command == "setup":
            setup_command()
        elif command == "process":
            if len(sys.argv) < 3:
                print("Usage: python -m src.main process <file.txt>")
                return
            process_book_command(sys.argv[2])
        elif command == "read":
            book_file = sys.argv[2] if len(sys.argv) > 2 else None
            send_mode = "--send" in sys.argv
            read_daily_command(book_file, send_mode)
        elif command == "status":
            status_command()
        elif command == "test-email":
            test_email_command()
        else:
            print(f"Unknown command: {command}")
            print("Run 'python -m src.main' for usage help")
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()