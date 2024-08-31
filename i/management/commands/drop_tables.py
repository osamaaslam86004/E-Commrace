# inside drop_tables.py

# Due to usage of models.CSCADE in models it is recommended not to drop the table of 
# Homepage app first. instead drop Monitors table, django will drop tables 
# Monitors model has foreign key/ManyToMany key to Homepage model. Otherwise use 
# python manage.py rest_db 

from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Deletes specified models from the app'

    def handle(self, *args, **options):
        models_to_delete = [
            'SocialAccount',
        ]

        for model_name in models_to_delete:
            model = apps.get_model('i', model_name)
            model.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'{model_name} deleted successfully!'))

        self.stdout.write(self.style.SUCCESS('Models deleted successfully!'))







"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps

class Command(BaseCommand):
    help = 'Drops specified tables from the database'

    def handle(self, *args, **options):
        models_to_drop = [
            'CustomUser',
            'UserProfile',
            'CustomerProfile',
            'SellerProfile',
            'CustomerServiceProfile',
            'ManagerProfile',
            'AdministratorProfile',
        ]

        with connection.schema_editor() as schema_editor:
            for model_name in models_to_drop:
                model = apps.get_model('Homepage', model_name)
                table_name = model._meta.db_table
                self.stdout.write(f"Dropping table: {table_name}")
                schema_editor.execute(f"DROP TABLE IF EXISTS {table_name}")

        self.stdout.write(self.style.SUCCESS('Tables dropped successfully!'))

"""




"""
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Drops specified tables from the database'

    def handle(self, *args, **options):
        tables_to_drop = ['axes_accesslog', 'axes_accessfailurelog', 'axes_accessattempt']

        with connection.schema_editor() as schema_editor:
            for table_name in tables_to_drop:
                self.stdout.write(f"Dropping table: {table_name}")
                schema_editor.execute(f"DROP TABLE IF EXISTS {table_name}")

        self.stdout.write(self.style.SUCCESS('Tables dropped successfully!'))
"""