import logging

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)


@shared_task(
    bind=True, max_retries=3, default_retry_delay=2
)  # Retry up to 3 times with a 60-second delay
def send_password_reset_email(self, email, reset_url):

    try:
        message = Mail(
            from_email=settings.CLIENT_EMAIL,
            to_emails=email,
            subject="Reset your password",
            html_content=f'Click the link to reset your password: <a href="{reset_url}">{reset_url}</a>',
        )
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        # return response

        # Check for a non-200 status code
        if response.status_code != 202:
            raise Exception(f"Non-200 response: {response.status_code}")

        logger.info(f"Email sent to {email}, response: {response.status_code}")

    except Exception as e:
        logger.error(f"Error while sending email: {str(e)}")

        # Check if we've exceeded maximum retries
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying... attempt {self.request.retries + 1}")
            raise self.retry(exc=e)  # Retry the task
        else:
            raise MaxRetriesExceededError(
                "Max retries exceeded for email sending task."
            )
