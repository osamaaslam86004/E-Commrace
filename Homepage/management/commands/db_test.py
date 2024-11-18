import random
from random import choice, randint
from faker import Faker
from django.core.management.base import BaseCommand
from django.utils import timezone
from Homepage.models import CustomUser, UserProfile
from i.models import (
    ComputerSubCategory,
    Monitors,
    ProductCategory,
    Review,
    Special_Features,
)

fake = Faker()


Product_Category = ProductCategory.objects.get(name="COMPUTER")
Computer_SubCategory = ComputerSubCategory.objects.get(name="MONITORS")


def random_mounting_type():
    return random.choice(
        [
            ("WALL_MOUNT", "Wall Mount"),
            ("DESK_MOUNT", "Desk Mount"),
        ]
    )


def random_brand():
    return random.choice(
        [
            ("SAMSUNG", "Samsung"),
            ("LG", "LG"),
            ("ASUS", "ASUS"),
            ("acer", "Acer"),
            ("Dell", "Dell"),
            ("ViewSonic", "ViewSonic"),
            ("msi", "MSI"),
            ("Spectre", "SPECTRE"),
        ],
    )


def random_aspect_ratio():
    return random.choice(["16:9", "16:10", "21:9"])


def max_display_resolution():
    return random.choice(
        [
            ("1280x1024", "1280 x 1024"),
            ("1680x1050", "1680 x 1050"),
            ("1920x1080", "1920 x 1080"),
            ("1920x1200", "1920 x 1200"),
            ("2560x1080", "2560 x 1080"),
            ("2560x1440", "2560 x 1440"),
            ("3440x1440", "3440 x 1440"),
            ("3840x2160", "3840 x 2160"),
            ("800x600", "800 x 600"),
        ],
    )


def screen_size():
    return random.choice(["24 inches", "27 inches", "32 inches"])


def monitor_type():
    return random.choice(["GAMING_MONITOR", "CARE_MONITOR", "HOME_OFFICE"])


def refresh_rate():
    return random.choice(
        [
            (240, "240 Hz"),
            (165, "165 Hz"),
            (160, "160 Hz"),
            (144, "144 Hz"),
            (120, "120 Hz"),
            (100, "100 Hz"),
            (75, "75 Hz"),
            (60, "60 Hz"),
        ],
    )


class Command(BaseCommand):
    help = "Populate the database with 10,000 Monitor records and their reviews"

    def handle(self, *args, **kwargs):

        # # Create 10,000 CustomUser instances with user_type "CustomerUser"
        users = []
        for _ in range(10000):
            email = fake.unique.email()
            user = CustomUser.objects.create(
                email=email,
                username=fake.unique.user_name(),
                password=fake.password(),
                user_type="SELLER",
            )

            self.stdout.write(self.style.SUCCESS(f"Successfully populated {_}th User!"))

            # Create UserProfile for each user as required
            UserProfile.objects.get_or_create(
                user=user,
                full_name=fake.name(),
                age=randint(18, 130),
                gender=choice(["Male", "Female", "Non-binary", "Other"]),
                phone_number="+923074649892",
                city=fake.city(),
                country=fake.country_code(),
                postal_code=fake.postcode(),
                shipping_address=fake.address(),
            )
            self.stdout.write(
                self.style.SUCCESS("Successfully populated User-Profile!")
            )

            users.append(user)

        # Create 10,000 Monitor instances linked to each CustomUser
        for i in range(10000):
            monitor = Monitors(
                monitor_id=i + 1,
                name=fake.word() + " Monitor",
                price=random.uniform(100.00, 999.99),
                mounting_type=random_mounting_type()[0],
                monitor_type=monitor_type(),
                max_display_resolution=max_display_resolution()[0],
                refresh_rate=refresh_rate()[0],
                brand=random_brand()[0],
                image_1=fake.image_url(),
                image_2=fake.image_url(),
                image_3=fake.image_url(),
                aspect_ratio=random_aspect_ratio(),
                screen_size=screen_size(),
                item_weight="11",
                voltage=220,
                color=fake.color_name(),
                hdmi_port=random.uniform(1.0, 4.0),
                built_speakers="yes",
                quantity_available=random.randint(1, 100),
                restock_threshold=random.randint(1, 10),
                user=users[i],  # Link the monitor to the corresponding CustomUser
                Product_Category=Product_Category,
                Computer_SubCategory=Computer_SubCategory,
            )
            monitor.save()

            # Add special features
            special_features = Special_Features.objects.all()[:3]
            monitor.special_features.set((list(special_features)))

            self.stdout.write(
                self.style.SUCCESS(f"Successfully populated {i}th Monitor!")
            )

            # Create 500 unique Review instances for each Monitor
            review_users = random.sample(list(users), 500)
            for index, user in enumerate(review_users):
                Review.objects.create(
                    user=user,
                    product=monitor,
                    rating=round(random.uniform(1.0, 5.0), 1),
                    status=True,
                    text=fake.text(max_nb_chars=200),
                    image_1=fake.image_url(),
                    image_2=fake.image_url(),
                    created_at=timezone.now(),
                )
            self.stdout.write(
                self.style.SUCCESS(f"Successfully populated {index}th Review!")
            )

        self.stdout.write(self.style.SUCCESS("Successfully populated the database!"))
