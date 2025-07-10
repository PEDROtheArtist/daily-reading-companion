"""Email service for sending daily reading chunks."""

import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

from ..models.core import Settings, BookChunk


class EmailService:
    """Service for sending daily reading chunks via email."""
    
    def __init__(self, settings: Settings):
        """Initialize email service with settings."""
        self.settings = settings
    
    def send_daily_chunk(self, 
                        book_title: str, 
                        chunk: dict, 
                        progress: dict) -> bool:
        """Send a daily reading chunk via email."""
        if not self.settings.enable_email:
            print("📧 Email delivery disabled")
            return False
        
        if not self.settings.sender_email or not self.settings.sender_password:
            print("❌ Email credentials not configured")
            return False
        
        try:
            # Create email content
            subject = f"Daily Reading: {book_title} - Day {progress['day']}"
            body = self._create_email_body(book_title, chunk, progress)
            
            # Send email
            return self._send_email(subject, body)
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def _create_email_body(self, book_title: str, chunk: dict, progress: dict) -> str:
        """Create the email body content."""
        # Calculate progress percentage
        progress_pct = (progress['current_chunk'] / progress['total_chunks']) * 100
        
        # Format reading time
        reading_time = chunk['estimated_reading_time']
        time_str = f"{reading_time:.1f} minutes"
        
        # Format the content for better email display
        formatted_content = self._format_content_for_email(chunk['content'])
        
        # Create HTML email body
        body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .title {{ color: #2c3e50; font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
        .stats {{ color: #6c757d; margin-bottom: 5px; }}
        .content {{ background-color: #ffffff; padding: 20px; border: 1px solid #dee2e6; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #6c757d; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title">📖 Daily Reading: {book_title}</div>
        <div class="stats">📅 Day {progress['day']}</div>
        <div class="stats">📊 Progress: {progress['current_chunk']}/{progress['total_chunks']} ({progress_pct:.1f}%)</div>
        <div class="stats">⏱️ Reading time: {time_str}</div>
        <div class="stats">📝 Words: {chunk['word_count']}</div>
    </div>
    
    <div class="content">
        {formatted_content}
    </div>
    
    <div class="footer">
        <p>Happy reading! 📚</p>
        <p>Sent by Daily Reading Companion<br>
        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>"""
        return body
    
    def _format_content_for_email(self, content: str) -> str:
        """Format content for HTML email display."""
        # Split into paragraphs
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Format headings (lines starting with ##)
            if paragraph.startswith('## '):
                heading = paragraph[3:].strip().upper()
                formatted_paragraphs.append(f'<h2 style="color: #2c3e50; margin-top: 20px; margin-bottom: 15px; font-size: 18px; font-weight: bold;">{heading}</h2>')
            else:
                # Convert single newlines within paragraphs to spaces
                paragraph = paragraph.replace('\n', ' ')
                
                # Convert markdown-style formatting to HTML
                paragraph = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', paragraph)
                paragraph = re.sub(r'\*(.*?)\*', r'<em>\1</em>', paragraph)
                
                formatted_paragraphs.append(f'<p style="margin-bottom: 15px; line-height: 1.6;">{paragraph}</p>')
        
        return '\n'.join(formatted_paragraphs)
    
    def _send_email(self, subject: str, body: str) -> bool:
        """Send email using SMTP."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.settings.sender_email
            msg['To'] = self.settings.user_email
            msg['Subject'] = subject
            
            # Add HTML body
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to server and send
            server = smtplib.SMTP(self.settings.smtp_server, self.settings.smtp_port)
            server.starttls()  # Enable TLS encryption
            server.login(self.settings.sender_email, self.settings.sender_password)
            
            text = msg.as_string()
            server.sendmail(self.settings.sender_email, self.settings.user_email, text)
            server.quit()
            
            print(f"📧 Email sent successfully to {self.settings.user_email}")
            return True
            
        except Exception as e:
            print(f"❌ SMTP Error: {e}")
            return False
    
    def test_email_connection(self) -> bool:
        """Test email connection and credentials."""
        if not self.settings.sender_email or not self.settings.sender_password:
            print("❌ Email credentials not configured")
            return False
        
        try:
            print("🔍 Testing email connection...")
            server = smtplib.SMTP(self.settings.smtp_server, self.settings.smtp_port)
            server.starttls()
            server.login(self.settings.sender_email, self.settings.sender_password)
            server.quit()
            
            print("✅ Email connection successful")
            return True
            
        except Exception as e:
            print(f"❌ Email connection failed: {e}")
            return False