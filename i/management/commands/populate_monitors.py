

from django.core.management.base import BaseCommand
from i.monitors import populate_monitors  # Import your function from monitors.py

class Command(BaseCommand):
    help = 'Populates Monitors table with initial data'

    def handle(self, *args, **kwargs):
        populate_monitors()
        self.stdout.write(self.style.SUCCESS('Monitors data populated successfully'))
