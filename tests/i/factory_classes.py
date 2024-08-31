import factory
import logging
import random
import factory.django
from faker import Faker
from i.models import (
    Monitors,
    ProductCategory,
    ComputerSubCategory,
    Special_Features,
    Review,
)
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory

fake = Faker()
# Disable Faker DEBUG logging
faker_logger = logging.getLogger("faker")
faker_logger.setLevel(logging.WARNING)


class ProductCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductCategory

    name = factory.LazyFunction(
        lambda: fake.random_element(ProductCategory.product_category_type_choices)[0]
    )


class ComputerSubCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComputerSubCategory

    name = factory.LazyFunction(
        lambda: fake.random_element(
            ComputerSubCategory.product_sub_category_type_choices
        )[0]
    )
    product_category = factory.SubFactory(ProductCategoryFactory)


class SpecialFeaturesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Special_Features

    name = factory.LazyFunction(
        lambda: fake.random_element(Special_Features.SPECIAL_FEATURES_CHOICES)[0]
    )


class MonitorsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Monitors

        # image_1 = factory.LazyAttribute(
        #     lambda _: ContentFile(fake.binary(length=1024), "test_image.jpg")
        # )
        # image_2 = factory.LazyAttribute(
        #     lambda _: ContentFile(fake.binary(length=1024), "test_image.jpg")
        # )
        # image_3 = factory.LazyAttribute(
        #     lambda _: ContentFile(fake.binary(length=1024), "test_image.jpg")
        # )

    image_1 = None
    image_2 = None
    image_3 = None
    name = factory.Faker("company")
    brand = factory.Faker(
        "random_element",
        elements=[
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
    aspect_ratio = factory.Faker("random_element", elements=["16:9", "16:10", "21:9"])
    max_display_resolution = factory.Faker(
        "random_element",
        elements=[
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
    screen_size = factory.Faker(
        "random_element", elements=["24 inches", "27 inches", "32 inches"]
    )
    monitor_type = factory.Faker(
        "random_element",
        elements=["GAMING_MONITOR", "CARE_MONITOR", "HOME_OFFICE"],
    )
    refresh_rate = factory.Faker(
        "random_element",
        elements=[
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
    mounting_type = factory.Faker(
        "random_element", elements=["Wall_Mount", "Desk_Mount"]
    )
    item_dimensions = factory.Faker("numerify", text="###x###x### mm")
    item_weight = factory.Faker("random_int", min=1, max=20)
    voltage = factory.Faker("random_int", min=100, max=240)
    color = factory.Faker("color_name")
    hdmi_port = factory.Faker("random_int", min=1, max=4)
    built_speakers = factory.Faker("random_element", elements=["yes", "no"])
    price = factory.Faker("random_number", digits=5, fix_len=True)
    quantity_available = factory.Faker("random_int", min=1, max=100)
    restock_threshold = factory.Faker("random_int", min=1, max=20)
    Product_Category = factory.SubFactory(ProductCategoryFactory)
    Computer_SubCategory = factory.SubFactory(ComputerSubCategoryFactory)
    user = factory.SubFactory(CustomUserOnlyFactory)
    monitor_id = factory.Sequence(lambda n: n + 1)

    @factory.post_generation
    def special_features(self, create, extracted, **kwargs):
        if not create:
            return

        # Create Special_Features if they don't exist
        if not Special_Features.objects.exists():
            for choice in Special_Features.SPECIAL_FEATURES_CHOICES:
                Special_Features.objects.create(name=choice[0])

        # Ensure there are enough features to sample
        if extracted:
            for feature in extracted:
                self.special_features.add(feature)
        else:
            features = list(Special_Features.objects.all())
            if len(features) < 3:
                raise ValueError(
                    "Not enough special features to assign to the monitor."
                )
            random_features = random.sample(features, 3)
            for feature in random_features:
                self.special_features.add(feature)


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    user = factory.SubFactory(CustomUserOnlyFactory)
    product = factory.SubFactory(MonitorsFactory)
    rating = factory.Faker(
        "pydecimal",
        left_digits=1,
        right_digits=1,
        positive=True,
        min_value=1,
        max_value=5,
    )
    status = factory.Faker("boolean", chance_of_getting_true=90)
    text = factory.Faker("paragraph")
    image_1 = factory.LazyAttribute(
        lambda _: "https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico"
    )
    image_2 = factory.LazyAttribute(
        lambda _: "https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico"
    )
    created_at = factory.Faker("date_time_this_year")
