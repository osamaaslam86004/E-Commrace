
from django.core.management.base import BaseCommand
from i.models import  ComputerSubCategory, ProductCategory
 


class Command(BaseCommand):
    help = 'Creates initial ProductCategory entries'

    def handle(self, *args, **kwargs):
        
        computer_category = ProductCategory.objects.get(name='COMPUTER')
        
        laptop_accessories, created = ComputerSubCategory.objects.get_or_create(
            name='LAPTOP_ACCESSORIES', product_category=computer_category)
        computer_and_tablets, created = ComputerSubCategory.objects.get_or_create(
            name='COMPUTERS_AND_TABLETS', product_category=computer_category)
        tablets_replacements_parts, created = ComputerSubCategory.objects.get_or_create(
            name='TABLETS_REPLACEMENT_PARTS', product_category=computer_category)
        servers, created = ComputerSubCategory.objects.get_or_create(
            name='SERVERS', product_category=computer_category)
        monitors, created = ComputerSubCategory.objects.get_or_create(
            name='MONITORS', product_category=computer_category)
        
        self.stdout.write(self.style.SUCCESS('Successfully created ComputerSubCategory entries'))

        