from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
from .services.pdf_service import PDFService
from .models import CV
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def send_cv_pdf_email(self, cv_id, recipient_email, sender_name=None):
    try:
        cv = CV.objects.get(id=cv_id)
        pdf_service = PDFService()
        pdf_buffer = pdf_service.generator.generate(cv)

        subject = f"CV of {cv.first_name} {cv.last_name}"
        message = f"""
Hello,

Please find attached the CV of {cv.first_name} {cv.last_name}.

Best regards,
{sender_name or 'CV Project Team'}
        """.strip()

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )

        email.attach(
            filename=f"{cv.first_name}_{cv.last_name}_CV.pdf",
            content=pdf_buffer.getvalue(),
            mimetype='application/pdf'
        )

        email.send()
        logger.info(f"CV PDF sent successfully to {recipient_email} for CV {cv_id}")

        return {
            'status': 'success',
            'message': f'CV PDF sent successfully to {recipient_email}',
            'cv_name': f"{cv.first_name} {cv.last_name}"
        }

    except CV.DoesNotExist:
        error_msg = f"CV with ID {cv_id} not found"
        logger.error(error_msg)
        return {
            'status': 'error',
            'message': error_msg
        }

    except Exception as e:
        error_msg = f"Failed to send CV PDF: {str(e)}"
        logger.error(error_msg)
        return {
            'status': 'error',
            'message': error_msg
        }

@shared_task
def debug_task():
    return "Celery is working correctly!"
