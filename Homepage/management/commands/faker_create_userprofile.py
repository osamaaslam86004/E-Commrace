from django.core.management.base import BaseCommand
from tests.Homepage.Homepage_factory import (
    UserProfileFactory_CustomUserFactory_Without_UserProfile_PostGeneration,
    CustomUserFactory_Without_UserProfile_PostGeneration,
)


class Command(BaseCommand):
    help = "Create one instance of each factory class and print out all attributes"

    def handle(self, *args, **kwargs):
        # Create an instance of CustomUserFactory_Without_UserProfile_PostGeneration
        custom_user = CustomUserFactory_Without_UserProfile_PostGeneration()
        self.print_instance_attributes(
            custom_user, "CustomUserFactory_Without_UserProfile_PostGeneration"
        )

        # Create an instance of UserProfileFactory_CustomUserFactory_Without_UserProfile_PostGeneration
        user_profile = (
            UserProfileFactory_CustomUserFactory_Without_UserProfile_PostGeneration()
        )
        self.print_instance_attributes(
            user_profile,
            "UserProfileFactory_CustomUserFactory_Without_UserProfile_PostGeneration",
        )

    def print_instance_attributes(self, instance, factory_name):
        print(f"\nAttributes for instance created by {factory_name}:")
        for field in instance._meta.get_fields():
            value = getattr(instance, field.name, None)
            print(f"{field.name}: {value}")
