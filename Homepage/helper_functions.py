import logging

import requests
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Mail, Personalization

logger = logging.getLogger(__name__)


def helper_function(generated_otp, phone_number) -> bool:

    # Twilio API endpoint
    endpoint = f"https://api.twilio.com/2010-04-01/Accounts/{settings.ACCOUNT_SID}/Messages.json"

    # Construct the request payload
    payload = {
        "From": settings.FROM_,
        "To": str(phone_number),  # otherwise 'PhoneNumber' object is not iterable
        "Body": f"Your OTP is: {generated_otp}",
    }

    # HTTP Basic Authentication credentials
    auth = (settings.ACCOUNT_SID, settings.AUTH_TOKEN)

    # Send HTTP POST request to Twilio
    # response = requests.post(endpoint, data=payload, auth=auth, verify=False)
    response = requests.post(endpoint, data=payload, auth=auth)

    # Check if request was successful
    if response.status_code == 201:
        return True
    elif response.status_code == 403:
        logger.warning("Twilio service unavailable: Test plan max usage reached.")
        return False
    else:
        logger.error(f"Twilio API error: {response.status_code} - {response.text}")
        return False


def delete_temporary_cookies(response):
    """Delete cookies with names temporary_cookie and otp_cookie."""

    # Delete the temporary_cookie
    response.delete_cookie("temporary_cookie", path="/")

    # Delete the otp_cookie
    response.delete_cookie("otp_cookie", path="/")

    return response


def send_dynamic_mail_template_in_production(email, reset_url):
    message = Mail(
        from_email=settings.CLIENT_EMAIL,
        to_emails=email,
        subject="Reset your password",
    )

    # Initialize SendGrid API client
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

    # Use SendGrid Dynamic Template
    message.template_id = (
        settings.PASSWORD_RESET_TEMPLATE_ID
    )  # Add template ID in settings.py

    # Personalization with dynamic variables
    personalization = Personalization()
    personalization.add_to(Email(email))

    personalization.dynamic_template_data = {"reset_url": reset_url}
    message.add_personalization(personalization)

    # Send the email
    response = sg.send(message)
    return response
