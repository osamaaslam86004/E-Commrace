# tests/test_models.py
import pytest
import logging
from django.contrib.auth import get_user_model
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from tests.i.factory_classes import ProductCategoryFactory
from book_.models import BookAuthorName, BookFormat, Review, Rating
from tests.books.books_factory_classes import (
    BookAuthorNameFactory,
    BookFormatFactory,
    ReviewFactory,
    RatingFactory,
)


# Disable Faker DEBUG logging
faker_logger = logging.getLogger("faker")
faker_logger.setLevel(logging.WARNING)


CustomUser = get_user_model()


@pytest.fixture
def build_setup_testing_Bookformat():

    def _build_setup_testing_Review(user_type):
        # create a user instance of given type
        user = CustomUserOnlyFactory(user_type=user_type)

        # Create a Product category for books
        product_category = ProductCategoryFactory(name="BOOKS")

        # Create the bookAuthorName
        book_author_name = BookAuthorNameFactory()

        # create BookFormat instance
        book = BookFormatFactory(
            user=user,
            book_author_name=book_author_name,
            product_category=product_category,
        )
        return product_category, user, book_author_name, book

    return _build_setup_testing_Review


@pytest.mark.django_db
def test_create_book_author_name(build_setup_testing_Bookformat):
    # build the data
    product_category, user, book_author_name, book = build_setup_testing_Bookformat(
        user_type="SELLER"
    )

    # Assertions
    assert book_author_name.book_name is not None
    assert book_author_name.author_name is not None
    assert book_author_name.about_author is not None
    assert book in book_author_name.format_name.all()


@pytest.mark.django_db
def test_create_book_format(build_setup_testing_Bookformat):
    # build the data
    product_category, user, book_author_name, book_format = (
        build_setup_testing_Bookformat(user_type="SELLER")
    )
    # Assertions
    assert book_format.user == user
    assert book_format.product_category == product_category
    assert book_format.format in ["AUDIO_CD", "SPIRAL_BOUND", "PAPER_BACK", "HARDCOVER"]
    assert book_format.is_new_available > 0
    assert book_format.is_used_available > 0
    assert book_format.publisher_name is not None
    assert (
        book_format.image_1 is not None
        and book_format.image_2 is not None
        and book_format.image_3 is not None
    )
    assert book_format.price is not None
    assert 1 <= book_format.price <= 999999.99


@pytest.mark.django_db
def test_book_format_on_cascade(build_setup_testing_Bookformat):
    # build the data
    product_category, user, book_author_name, book_format = (
        build_setup_testing_Bookformat(user_type="SELLER")
    )
    # deleting the user, it will also delete Bookformat, BookAuthorname
    user.delete()

    # Assertions
    with pytest.raises(BookFormat.DoesNotExist):
        BookFormat.objects.get(id=book_format.id)


@pytest.mark.django_db
def test_book_author_name_on_cascade(build_setup_testing_Bookformat):
    # build the data
    product_category, user, book_author_name, book_format = (
        build_setup_testing_Bookformat(user_type="SELLER")
    )
    # deleting the user, it will also delete Bookformat, BookAuthorname
    user.delete()

    # Assertions
    with pytest.raises(BookAuthorName.DoesNotExist):
        assert BookFormat.objects.get(id=book_format.id)


@pytest.mark.django_db
def test_create_review(build_setup_testing_Bookformat):
    # build the data
    product_category, user, book_author_name, book_format = (
        build_setup_testing_Bookformat(user_type="SELLER")
    )
    review = ReviewFactory(user=user, book_format=book_format)
    assert review.user == user
    assert review.book_format == book_format
    assert review.content is not None
    assert review.image_1 is not None and review.image_2 is not None


@pytest.mark.django_db
def test_create_rating(build_setup_testing_Bookformat):
    # build the data
    product_category, user, book_author_name, book_format = (
        build_setup_testing_Bookformat(user_type="SELLER")
    )
    # create a Review instance
    review = ReviewFactory(user=user, book_format=book_format)

    # create a Rating instance
    rating = RatingFactory(user=user, book_format=book_format)
    assert rating.user == user
    assert rating.book_format == book_format
    assert 1 <= rating.rating <= 5


@pytest.mark.django_db
def test_review_rating_on_cascade(build_setup_testing_Bookformat):
    # build the data
    product_category, user, book_author_name, book_format = (
        build_setup_testing_Bookformat(user_type="SELLER")
    )
    # creating a Review instance
    review = ReviewFactory(user=user, book_format=book_format)

    # create a Review instance
    rating = RatingFactory(user=user, book_format=book_format)

    # deleting the user will delete the review and rating
    user.delete()

    # Confirms Review instance is deleted
    with pytest.raises(Review.DoesNotExist):
        Review.objects.get(id=review.id)

    # Confirms Rating instance is deleted
    with pytest.raises(Rating.DoesNotExist):
        Rating.objects.get(id=rating.id)
