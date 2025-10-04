from celery import shared_task
from django.conf import settings
from .services.pdf_service import PDFService
from .services.email_service import get_email_service
from .models import CV
from .utils.cv_data_utils import prepare_cv_data
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def send_cv_pdf_email(self, cv_id, recipient_email, sender_name=None):
    try:
        cv = CV.objects.get(id=cv_id)

        # Prepare CV data
        cv_data = prepare_cv_data(cv)

        # Generate PDF
        pdf_service = PDFService()
        pdf_buffer = pdf_service.generator.generate(cv)
        pdf_content = pdf_buffer.getvalue()

        # Send email using EmailService
        email_service = get_email_service()
        result = email_service.send_cv_pdf_email(
            cv_data=cv_data,
            recipient_email=recipient_email,
            sender_name=sender_name,
            pdf_content=pdf_content
        )

        if result['status'] == 'success':
            logger.info(f"CV PDF sent successfully to {recipient_email} for CV {cv_id}")
            result['cv_name'] = f"{cv.first_name} {cv.last_name}"

        return result

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
