import logging
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self):
        self.settings = get_settings()
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: Optional[str] = None
    ) -> bool:
        """Send email via SMTP or fallback to console/Telegram"""
        if self.settings.email_enabled and self.settings.smtp_host:
            return await self._send_via_smtp(to_email, subject, body, html)
        else:
            return await self._send_via_console(to_email, subject, body)
    
    async def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: Optional[str] = None
    ) -> bool:
        """Send email via SMTP"""
        try:
            import aiosmtplib
            from email.message import EmailMessage
            
            message = EmailMessage()
            message["From"] = f"{self.settings.smtp_from_name} <{self.settings.smtp_from_email}>"
            message["To"] = to_email
            message["Subject"] = subject
            
            if html:
                message.add_alternative(html, subtype="html")
                message.add_alternative(body, subtype="plain")
            else:
                message.set_content(body)
            
            await aiosmtplib.send(
                message,
                hostname=self.settings.smtp_host,
                port=self.settings.smtp_port,
                username=self.settings.smtp_username,
                password=self.settings.smtp_password,
                start_tls=True,
            )
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}")
            return await self._send_via_console(to_email, subject, body)
    
    async def _send_via_console(
        self,
        to_email: str,
        subject: str,
        body: str
    ) -> bool:
        """Fallback: Log email to console and optionally send to Telegram"""
        logger.info(f"EMAIL TO: {to_email}")
        logger.info(f"SUBJECT: {subject}")
        logger.info(f"BODY: {body}")
        logger.info("=" * 50)
        
        if self.settings.telegram_bot_token and self.settings.telegram_chat_id:
            await self._send_via_telegram(to_email, subject, body)
        
        return True
    
    async def _send_via_telegram(
        self,
        to_email: str,
        subject: str,
        body: str
    ) -> bool:
        """Send email content to Telegram bot as fallback"""
        try:
            import httpx
            message = f"📧 EMAIL\n\nTo: {to_email}\nSubject: {subject}\n\n{body}"
            url = f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage"
            await httpx.post(url, json={"chat_id": self.settings.telegram_chat_id, "text": message})
            logger.info(f"Email sent to Telegram: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send to Telegram: {e}")
            return False


email_sender = EmailSender()
