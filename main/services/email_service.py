from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        if not settings.EMAIL_HOST_USER:
            raise ValueError("Email configuration is required")

        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.reply_to = getattr(settings, 'REPLY_TO_EMAIL', self.from_email)

    def send_cv_pdf_email(self, cv_data: Dict[str, Any], recipient_email: str,
                         sender_name: Optional[str] = None, pdf_content: bytes = None) -> Dict[str, Any]:
        try:
            subject = self._generate_subject(cv_data, sender_name)
            html_content = self._generate_html_content(cv_data, sender_name)

            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=self.from_email,
                to=[recipient_email],
                reply_to=[self.reply_to]
            )

            email.content_subtype = "html"

            if pdf_content:
                filename = f"{cv_data['first_name']}_{cv_data['last_name']}_CV.pdf"
                email.attach(filename, pdf_content, 'application/pdf')

            email.send()

            logger.info(f"CV PDF email sent successfully to {recipient_email}")
            return {
                'status': 'success',
                'message': f'CV PDF sent successfully to {recipient_email}',
                'recipient': recipient_email
            }

        except Exception as e:
            logger.error(f"Failed to send CV PDF email: {e}")
            return {
                'status': 'error',
                'message': f'Failed to send email: {str(e)}',
                'recipient': recipient_email
            }

    def _generate_subject(self, cv_data: Dict[str, Any], sender_name: Optional[str] = None) -> str:
        cv_name = f"{cv_data['first_name']} {cv_data['last_name']}"
        if sender_name:
            return f"CV of {cv_name} from {sender_name}"
        return f"CV of {cv_name}"

    def _generate_html_content(self, cv_data: Dict[str, Any], sender_name: Optional[str] = None) -> str:
        context = {
            'cv': cv_data,
            'sender_name': sender_name,
            'site_name': getattr(settings, 'SITE_NAME', 'CV Project')
        }

        try:
            return render_to_string('main/emails/cv_pdf_email.html', context)
        except Exception:
            # Fallback to simple HTML if template not found
            return self._generate_fallback_html(cv_data, sender_name)

    def _generate_fallback_html(self, cv_data: Dict[str, Any], sender_name: Optional[str] = None) -> str:
        cv_name = f"{cv_data['first_name']} {cv_data['last_name']}"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>CV from CV Project</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Hello!</h2>
                <p>Please find attached the CV of <strong>{cv_name}</strong>.</p>
                {f'<p><strong>Sent by:</strong> {sender_name}</p>' if sender_name else ''}
                <p>Best regards,<br>CV Project Team</p>
            </div>
        </body>
        </html>
        """
        return html.strip()

def get_email_service() -> EmailService:
    return EmailService()
