from django.apps import AppConfig
from django.db.models.signals import post_migrate

class HomepageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Homepage'

    def ready(self):
        # Import the initialization function from your script
        from Homepage.initialize_permissions import initialize_groups_permissions

        # Connect to the post_migrate signal and execute the initialization function
        post_migrate.connect(initialize_groups_permissions, sender=self)

        # Place your additional code here, including the signal connection
        # for assigning groups based on user-types

        # from .import signals
        import Homepage.signals  # Import your signal handler module


      
