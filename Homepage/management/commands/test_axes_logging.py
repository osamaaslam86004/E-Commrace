import logging

from axes.utils import reset
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Tests logging for django-axes"

    def handle(self, *args, **kwargs):
        logger = logging.getLogger("axes")

        # Simulate a failed login attempt
        username = "testuser"  # Replace with an actual username if needed
        user = get_user_model().objects.filter(username=username).first()

        if user:
            # Simulate a failed login attempt
            try:
                attempts = reset(user)
                logger.error(
                    f"Simulated failed login attempt for user: {username}. Attempts: {attempts}"
                )
            except Exception as e:
                logger.error(f" Exception in reset '{e}'")
        else:
            logger.error(f"User  '{username}' does not exist.")
