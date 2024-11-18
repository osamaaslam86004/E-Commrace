import io
import logging

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from PIL import Image

from book_.forms import (BookAuthorNameForm, BookFormatForm, RatingForm,
                         ReviewForm)
from tests.books.books_factory_classes import (BookAuthorNameFactory,
                                               BookFormatFactory,
                                               RatingFactory, ReviewFactory)
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from tests.i.factory_classes import ProductCategoryFactory

fake = Faker()
# Disable Faker DEBUG logging
faker_logger = logging.getLogger("faker")
faker_logger.setLevel(logging.WARNING)


@pytest.fixture
def create_image_size_greater_one_mb():

    # Create an image file using Pillow with size > 1MB
    image = Image.new("RGB", (12080, 8080), color="red")
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="JPEG", quality=100)
    image_bytes.seek(0)

    # Create a SimpleUploadedFile from the image bytes
    uploaded_file = SimpleUploadedFile(
        "test_image.jpeg", image_bytes.read(), content_type="image/jpeg"
    )

    assert uploaded_file is not None
    # Debug print
    print(f"Uploaded file size: {len(uploaded_file)} bytes")

    return uploaded_file


@pytest.fixture
def create_image_tiff():

    # Create an image file using Pillow
    image = Image.new("RGB", (100, 100), color="red")
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="TIFF")
    image_bytes.seek(0)

    # Create a SimpleUploadedFile from the image bytes
    uploaded_file = SimpleUploadedFile(
        "test_image.tiff", image_bytes.read(), content_type="image/tiff"
    )

    assert uploaded_file is not None
    # Debug print
    print(f"Uploaded file size: {len(uploaded_file)} bytes")

    return uploaded_file


@pytest.fixture
def create_image():

    # Create an image file using Pillow with size > 1MB
    image = Image.new("RGB", (100, 100), color="red")
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="JPEG", quality=100)
    image_bytes.seek(0)

    # Create a SimpleUploadedFile from the image bytes
    uploaded_file = SimpleUploadedFile(
        "test_image.jpeg", image_bytes.read(), content_type="image/jpeg"
    )

    assert uploaded_file is not None
    # Debug print
    print(f"Uploaded file size: {len(uploaded_file)} bytes")

    return uploaded_file


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


@pytest.fixture
def book_author_name_form_data(build_setup_testing_Bookformat):
    def _book_author_name_form_data():
        product_category, user, book_author_name, book_format = (
            build_setup_testing_Bookformat(user_type="SELLER")
        )
        # Form data dictionary
        form_data = {
            "book_name": book_author_name.book_name,
            "author_name": book_author_name.author_name,
            "about_author": book_author_name.about_author,
            "language": book_author_name.language,
        }
        return form_data, product_category, user, book_author_name, book_format

    return _book_author_name_form_data


@pytest.fixture
def book_format_form_data(build_setup_testing_Bookformat, create_image):
    def _book_format_form_data():
        product_category, user, book_author_name, book_format = (
            build_setup_testing_Bookformat(user_type="SELLER")
        )

        # Form data dictionary
        form_data = {
            "format": book_format.format,
            "is_new_available": book_format.is_new_available,
            "is_used_available": book_format.is_used_available,
            "publisher_name": book_format.publisher_name,
            "publishing_date": book_format.publishing_date,
            "edition": book_format.edition,
            "length": book_format.length,
            "narrator": book_format.narrator,
            "price": float(book_format.price),
            "is_active": book_format.is_active,
            "restock_threshold": book_format.restock_threshold,
            "image_1": create_image,
            "image_2": create_image,
            "image_3": create_image,
        }
        return form_data, product_category, user, book_author_name, book_format

    return _book_format_form_data


@pytest.fixture
def review_form_data(build_setup_testing_Bookformat):
    def _review_form_data():
        # build the data
        product_category, user, book_author_name, book_format = (
            build_setup_testing_Bookformat(user_type="SELLER")
        )
        # creating a Review instance
        # review = ReviewFactory(user=user, book_format=book_format)
        review = ReviewFactory()

        form_data = {
            "title": review.title,
            "content": review.content,
            "image_1": review.image_1,
            "image_2": review.image_2,
        }
        return form_data, product_category, user, book_author_name, book_format

    return _review_form_data


@pytest.fixture
def rating_form_data(build_setup_testing_Bookformat):
    def _rating_form_data():
        # build the data
        product_category, user, book_author_name, book_format = (
            build_setup_testing_Bookformat(user_type="SELLER")
        )
        # create a Review instance
        # rating = RatingFactory(user=user, book_format=book_format)
        rating = RatingFactory()

        form_data = {"rating": float(rating.rating)}
        return form_data, product_category, user, book_author_name, book_format

    return _rating_form_data


def generate_paragraph(input):

    paragraph = fake.text(input)

    while len(paragraph) < input:
        paragraph += fake.sentence(1)[0] + " "

    return paragraph


@pytest.mark.django_db
def test_Book_Author_Name_Form(book_author_name_form_data):
    data, product_category, user, book_author_name, book_format = (
        book_author_name_form_data()
    )

    form = BookAuthorNameForm(data=data)
    assert form.is_valid()


@pytest.mark.django_db
def test_Book_Format_Form(book_format_form_data):
    data, product_category, user, book_author_name, book_format = (
        book_format_form_data()
    )

    form = BookFormatForm(data=data)
    assert form.is_valid()


@pytest.mark.django_db
def test_Book_Format_Form_image_upload(book_format_form_data, create_image):
    data, product_category, user, book_author_name, book_format = (
        book_format_form_data()
    )

    # binding images with the form data
    data["image_1"] = create_image
    data["image_2"] = create_image
    data["image_3"] = create_image

    assert len(data["image_1"]) > 0
    assert len(data["image_2"]) > 0
    assert len(data["image_3"]) > 0

    form = BookFormatForm(data=data)
    assert form.is_valid()


@pytest.mark.django_db
def test_Book_Author_Name_Form_save(book_author_name_form_data):
    data, product_category, user, book_author_name, book_format = (
        book_author_name_form_data()
    )

    form = BookAuthorNameForm(data=data)
    assert form.is_valid()

    form.is_valid()
    form.save()


@pytest.mark.django_db
class Test_Clean_Mthods_BookAuthorName:
    def test_clean_author_name(self, book_author_name_form_data):
        data, product_category, user, book_author_name, book_format = (
            book_author_name_form_data()
        )

        data["author_name"] = generate_paragraph(60)
        assert len(data["author_name"]) > 50

        form = BookAuthorNameForm(data=data)
        assert not form.is_valid()

    def test_clean_book_name(self, book_author_name_form_data):
        data, product_category, user, book_author_name, book_format = (
            book_author_name_form_data()
        )

        data["book_name"] = generate_paragraph(100)

        form = BookAuthorNameForm(data=data)
        assert not form.is_valid()

    def test_clean_about_author(self, book_author_name_form_data):
        data, product_category, user, book_author_name, book_format = (
            book_author_name_form_data()
        )

        data["about_author"] = generate_paragraph(510)

        form = BookAuthorNameForm(data=data)
        assert not form.is_valid()

    def test_clean_language(self, book_author_name_form_data):
        data, product_category, user, book_author_name, book_format = (
            book_author_name_form_data()
        )

        data["language"] = generate_paragraph(25)

        form = BookAuthorNameForm(data=data)
        assert not form.is_valid()


@pytest.mark.django_db
class Test_Clean_Mthods_BookFormat:

    @pytest.mark.parametrize(
        "format, is_valid", [(None, False), ("invalid", False), ("HARDCOVER", True)]
    )
    def test_clean_format(self, format, is_valid, book_format_form_data):

        data, product_category, user, book_author_name, book_format = (
            book_format_form_data()
        )

        data["format"] = format
        form = BookFormatForm(data=data)
        assert form.is_valid() == is_valid

    @pytest.mark.parametrize(
        "is_new_available, is_valid",
        [(None, False), ("invalid", False), (-5, False), (21474836470, False)],
    )
    def test_clean_is_new_available(
        self, is_new_available, is_valid, book_format_form_data
    ):

        form_data, product_category, user, book_author_name, book_format = (
            book_format_form_data()
        )

        form_data["is_new_available"] = is_new_available
        form = BookFormatForm(data=form_data)
        form.is_valid() == is_valid

    @pytest.mark.parametrize(
        "is_used_available, is_valid",
        [(None, False), ("invalid", False), (-5, False), (21474836470, False)],
    )
    def test_clean_is_used_available(
        self, is_used_available, is_valid, book_format_form_data
    ):

        form_data, product_category, user, book_author_name, book_format = (
            book_format_form_data()
        )

        form_data["is_used_available"] = is_used_available
        form = BookFormatForm(data=form_data)
        form.is_valid() == is_valid

    @pytest.mark.parametrize(
        "publisher_name, is_valid",
        [
            (None, False),
            ("invalid", True),
            (-5, False),
            (10, False),
            (fake.text(max_nb_chars=110), False),
            (fake.text(max_nb_chars=100), True),
        ],
    )
    def test_clean_publisher_name(
        self, publisher_name, is_valid, book_format_form_data
    ):

        form_data, product_category, user, book_author_name, book_format = (
            book_format_form_data()
        )

        form_data["publisher_name"] = publisher_name
        form = BookFormatForm(data=form_data)
        form.is_valid() == is_valid

    @pytest.mark.parametrize(
        "narrator, is_valid",
        [
            (None, True),
            (-5, True),
            (fake.text(max_nb_chars=30), False),
            (fake.text(max_nb_chars=20), True),
        ],
    )
    def test_clean_narrator(self, narrator, is_valid, book_format_form_data):

        form_data, product_category, user, book_author_name, book_format = (
            book_format_form_data()
        )

        form_data["narrator"] = narrator
        form = BookFormatForm(data=form_data)
        form.is_valid() == is_valid

    @pytest.mark.parametrize(
        "price, is_valid",
        [
            (None, False),
            (-5, False),
            (1, False),
            (999999.99, True),
            (999999.999, False),
            (9999990.99, False),
        ],
    )
    def test_clean_price(self, price, is_valid, book_format_form_data):

        form_data, product_category, user, book_author_name, book_format = (
            book_format_form_data()
        )

        form_data["price"] = price
        form = BookFormatForm(data=form_data)
        form.is_valid() == is_valid

    @pytest.mark.parametrize(
        "restock_threshold, is_valid",
        [
            (None, False),
            (-5, False),
            (1, False),
            (9, True),
            (21474836470, False),
        ],
    )
    def test_clean_restock_threshold(
        self, restock_threshold, is_valid, book_format_form_data
    ):

        form_data, product_category, user, book_author_name, book_format = (
            book_format_form_data()
        )

        form_data["restock_threshold"] = restock_threshold
        form = BookFormatForm(data=form_data)
        form.is_valid() == is_valid

    def test_clean_image_1(self, book_format_form_data):
        form_data, product_category, user, book_author_name, book_format = (
            book_format_form_data()
        )

        # form_data["image_1"] = None
        print(f"form data: {form_data}")

        form = BookFormatForm(data=form_data)
        print(f"errors: {form.errors}")
        assert form.is_valid()

    def test_image_1_extension(self, create_image_tiff, book_format_form_data):
        form_data, product_category, user, book_author_name, book_format = (
            book_format_form_data()
        )

        files = {
            "image_1": create_image_tiff,
            "image_2": create_image_tiff,
            "image_3": create_image_tiff,
        }

        form = BookFormatForm(data=form_data, files=files)

        # Ensure the form is not valid and check for extension error
        assert not form.is_valid()
        assert "image_1" in form.errors
        assert (
            "Allowed extensions 'png', 'jpeg', 'jpg', 'webp'"
            in form.errors["image_1"][0]
        )

    def test_clean_image_2(self, book_format_form_data):
        form_data, product_category, user, book_author_name, book_format = (
            book_format_form_data()
        )

        form_data["image_2"] = None
        form = BookFormatForm(data=form_data)
        assert form.is_valid()

    def test_clean_image_3(self, book_format_form_data):
        form_data, product_category, user, book_author_name, book_format = (
            book_format_form_data()
        )

        form_data["image_3"] = None
        form = BookFormatForm(data=form_data)
        assert form.is_valid()


@pytest.mark.django_db
class Test_ReviewAndRatingForms:
    def test_review_form_valid_data(self):
        data = {
            "image_1": None,
            "image_2": None,
            "title": "Great book!",
            "content": "I really enjoyed reading this book.",
            "rating": 4,
        }
        files = {"image_1": None, "image_2": None}
        form = ReviewForm(data=data, files=files)
        assert form.is_valid()

    def test_review_form_missing_required_field(self, create_image: SimpleUploadedFile):
        data = {
            "image_1": create_image,
            "image_2": create_image,
            "title": "",
            "content": "I really enjoyed reading this book.",
            "rating": None,
        }

        files = {"image_1": create_image, "image_2": create_image}
        form = ReviewForm(data=data, files=files)
        assert form.is_valid()

    def test_rating_form_valid_data(self):
        data = {
            "rating": 4,
        }
        form = RatingForm(data=data)
        assert form.is_valid()

    def test_rating_form_invalid_rating(self):
        data = {
            "rating": 6,
        }
        form = RatingForm(data=data)
        assert not form.is_valid()
        assert "rating" in form.errors
        assert "Ensure this value is less than or equal to 5" in str(form.errors)


@pytest.mark.django_db
def test_book_format_form_image_size_validation(
    create_image_size_greater_one_mb: SimpleUploadedFile, book_format_form_data
):

    book_data, product_category, user, book_author_name, book_format = (
        book_format_form_data()
    )

    assert len(create_image_size_greater_one_mb) > 1048576

    files = {
        "image_1": create_image_size_greater_one_mb,
        "image_2": create_image_size_greater_one_mb,
        "image_3": create_image_size_greater_one_mb,
    }

    book_data["image_1"] = create_image_size_greater_one_mb
    book_data["image_2"] = create_image_size_greater_one_mb
    book_data["image_3"] = create_image_size_greater_one_mb

    # Initialize the form with POST data and file data
    form = BookFormatForm(data=book_data, files=files)

    # Check if the form is invalid due to image size
    # with pytest.raises(ValidationError):
    assert not form.is_valid(), "Form should be invalid due to large image size"
    assert "File size must be less than 1MB." in str(
        form.errors
    ), "Expected file size validation error"
