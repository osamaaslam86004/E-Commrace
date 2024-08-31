# factories.py
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from tests.i.factory_classes import ProductCategoryFactory
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from book_.models import BookAuthorName, BookFormat, Review, Rating

fake = Faker()


class BookAuthorNameFactory(DjangoModelFactory):
    class Meta:
        model = BookAuthorName

    book_name = factory.Faker("sentence", nb_words=4)
    author_name = factory.Faker("name")
    about_author = factory.Faker("text", max_nb_chars=500)
    language = "English"


class BookFormatFactory(DjangoModelFactory):
    class Meta:
        model = BookFormat

    book_author_name = factory.SubFactory(BookAuthorNameFactory)
    user = factory.SubFactory(CustomUserOnlyFactory)
    product_category = factory.SubFactory(ProductCategoryFactory)
    format = factory.Iterator([choice[0] for choice in BookFormat.FORMAT_CHOICES])
    is_new_available = factory.Faker("random_int", min=1, max=100)
    is_used_available = factory.Faker("random_int", min=1, max=100)
    publisher_name = factory.Faker("company")
    publishing_date = factory.Faker("date")
    edition = factory.Faker("word")
    length = factory.Faker("random_int", min=50, max=1000)
    narrator = factory.Faker("name")
    price = factory.Faker(
        "pydecimal",
        left_digits=6,
        right_digits=2,
        positive=True,
        min_value=1,
        max_value=999999.99,
    )
    is_active = True
    restock_threshold = 9
    image_1 = "https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico"
    image_2 = "https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico"
    image_3 = "https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico"


class ReviewFactory(DjangoModelFactory):
    class Meta:
        model = Review

    user = factory.SubFactory(CustomUserOnlyFactory)
    book_format = factory.SubFactory(BookFormatFactory)
    title = factory.Faker("sentence", nb_words=6)
    content = factory.Faker("text")
    status = True
    image_1 = "https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico"
    image_2 = "https://res.cloudinary.com/dh8vfw5u0/image/upload/v1702231959/rmpi4l8wsz4pdc6azeyr.ico"


class RatingFactory(DjangoModelFactory):
    class Meta:
        model = Rating

    user = factory.SubFactory(CustomUserOnlyFactory)
    book_format = factory.SubFactory(BookFormatFactory)
    rating = factory.Faker(
        "pydecimal",
        left_digits=1,
        right_digits=1,
        positive=True,
        min_value=1,
        max_value=5,
    )
