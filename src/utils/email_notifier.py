"""
Email notification system using Gmail SMTP
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

class EmailNotifier:
    """
    Sends email notifications for post approvals
    """
    
    def __init__(self):
        self.gmail_address = os.getenv("GMAIL_ADDRESS")
        self.gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        self.app_base_url = os.getenv("APP_BASE_URL", "https://your-app.vercel.app")
        
        if not self.gmail_address or not self.gmail_password:
            raise ValueError("GMAIL_ADDRESS and GMAIL_APP_PASSWORD must be set in .env file")
    
    def send_notification(
        self,
        recipient: str,
        post_id: str,
        post_text: str,
        mode: str
    ) -> bool:
        """
        Send notification email when post is generated
        
        Args:
            recipient: Email address to send to
            post_id: UUID of the post
            post_text: The generated post text
            mode: Generation mode
            
        Returns:
            True if sent successfully, False otherwise
        """
        subject = "New Threads Post Ready for Approval"
        
        approval_url = f"{self.app_base_url}/approve/{post_id}"
        approve_link = f"{approval_url}?action=approve"
        reject_link = f"{approval_url}?action=reject"
        
        # Truncate post text for email preview
        preview_text = post_text[:200] + "..." if len(post_text) > 200 else post_text
        
        body = f"""
A new post has been generated and is waiting for your approval.

Generation Mode: {mode.upper()}

Post Preview:
{preview_text}

---
Full Post ({len(post_text)} characters):
{post_text}
---

Approve: {approve_link}
Reject: {reject_link}

View All Pending: {self.app_base_url}
"""
        
        return self._send_email(recipient, subject, body)
    
    def send_confirmation(
        self,
        recipient: str,
        post_text: str,
        thread_url: Optional[str] = None
    ) -> bool:
        """
        Send confirmation email when post is published
        
        Args:
            recipient: Email address to send to
            post_text: The published post text
            thread_url: Optional Threads URL
            
        Returns:
            True if sent successfully, False otherwise
        """
        subject = "Threads Post Published Successfully"
        
        body = f"""
Your post has been published to Threads!

Post:
{post_text}

"""
        
        if thread_url:
            body += f"View on Threads: {thread_url}\n"
        
        return self._send_email(recipient, subject, body)
    
    def _send_email(self, recipient: str, subject: str, body: str) -> bool:
        """
        Internal method to send email via Gmail SMTP
        
        Args:
            recipient: Email address to send to
            subject: Email subject
            body: Email body text
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.gmail_address
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.gmail_address, self.gmail_password)
            text = msg.as_string()
            server.sendmail(self.gmail_address, recipient, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False




