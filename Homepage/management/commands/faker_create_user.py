import random
import string
from django.core.management.base import BaseCommand
from faker import Faker
from Homepage.models import CustomUser


class Command(BaseCommand):
    help = "Create a user with random and unique credentials"

    def handle(self, *args, **kwargs):
        faker = Faker()

        username = faker.user_name()
        email = faker.unique.email()
        password = "".join(random.choices(string.ascii_letters + string.digits, k=10))

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type="SELLER",  # You can change this to any user type you want
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created user with username: {username}, email: {email}, password: {password}"
            )
        )
