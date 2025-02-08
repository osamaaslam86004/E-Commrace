import logging

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Triggers an error to test logging"

    def handle(self, *args, **kwargs):
        logger = logging.getLogger("django")
        logger.error("This is a test error triggered by the management command.")
        raise Exception("This is a test error from the management command!")
