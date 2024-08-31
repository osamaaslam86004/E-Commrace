
from django.core.management.base import BaseCommand
from i.models import ProductCategory

class Command(BaseCommand):
    help = 'Creates initial ProductCategory entries'

    def handle(self, *args, **kwargs):
        computer_category, created = ProductCategory.objects.get_or_create(name='COMPUTER')
        electronics_category, created = ProductCategory.objects.get_or_create(name='ELECTRONICS')
        Books_category, created = ProductCategory.objects.get_or_create(name='BOOKS')
        self.stdout.write(self.style.SUCCESS('Successfully created ProductCategory entries'))




    


