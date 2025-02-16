import os

import django

# Set up Django environment
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "iii.settings"
)  # Replace 'iii.settings' with your actual settings module
django.setup()

from django.apps import apps

# Get all models
models = apps.get_models()

# List table names
table_names = [model._meta.db_table for model in models]
print("Tables in the database:")
for table in table_names:
    print(table)
