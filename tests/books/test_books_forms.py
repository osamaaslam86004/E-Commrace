import pytest
import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from tests.books.books_factory_classes import (
    BookAuthorNameFactory,
    BookFormatFactory,
    ReviewFactory,
    RatingFactory,
)
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from tests.i.factory_classes import ProductCategoryFactory
from book_.forms import BookAuthorNameForm, BookFormatForm, ReviewForm, RatingForm
from django.core.exceptions import ValidationError
from faker import Faker
import logging
from datetime import date


fake = Faker()
# Disable Faker DEBUG logging
faker_logger = logging.getLogger("faker")
faker_logger.setLevel(logging.WARNING)


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
            # user=user,
            # book_author_name=book_author_name,
            # product_category=product_category,
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
def book_format_form_data(build_setup_testing_Bookformat):
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
            "image_1": book_format.image_1,
            "image_2": book_format.image_2,
            "image_3": book_format.image_3,
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


@pytest.fixture
def create_image():

    # Create an image file using Pillow
    image = Image.new("RGB", (100, 100), color="red")
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="JPEG")
    image_bytes.seek(0)

    # Create a SimpleUploadedFile from the image bytes
    uploaded_file = SimpleUploadedFile(
        "test_image.jpg", image_bytes.read(), content_type="image/jpeg"
    )

    assert uploaded_file is not None
    # Debug print
    print(f"Uploaded file size: {len(uploaded_file)} bytes")

    return uploaded_file


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
        # print(f"data--------- : {data}")

        # creating author name with len > 50
        data["author_name"] = generate_paragraph(60)
        assert len(data["author_name"]) > 50

        with pytest.raises(ValidationError):
            form = BookAuthorNameForm(data=data)
            form.is_valid()

    def test_clean_book_name(self, book_author_name_form_data):
        data, product_category, user, book_author_name, book_format = (
            book_author_name_form_data()
        )

        # creating author name with len > 50
        data["book_name"] = generate_paragraph(255)

        with pytest.raises(ValidationError):
            form = BookAuthorNameForm(data=data)
            form.is_valid()

    def test_clean_about_author(self, book_author_name_form_data):
        data, product_category, user, book_author_name, book_format = (
            book_author_name_form_data()
        )

        # creating author name with len > 50
        data["about_author"] = generate_paragraph(500)

        with pytest.raises(ValidationError):
            form = BookAuthorNameForm(data=data)
            form.is_valid()

    def test_clean_language(self, book_author_name_form_data):
        data, product_category, user, book_author_name, book_format = (
            book_author_name_form_data()
        )

        # creating author name with len > 50
        data["language"] = generate_paragraph(15)

        with pytest.raises(ValidationError):
            form = BookAuthorNameForm(data=data)
            form.is_valid()


@pytest.mark.django_db
class Test_Clean_Mthods_BookFormat:
    def test_clean_book_author_name(self, book_format_form_data):
        data, product_category, user, book_author_name, book_format = (
            book_format_form_data()
        )

        # creating book author name with len > 0
        data["book_author_name"] = None

        with pytest.raises(ValidationError):
            form = BookAuthorNameForm(data=data)
            form.is_valid()

    def test_clean_format(self, book_format_form_data):
        data, product_category, user, book_author_name, book_format = (
            book_format_form_data()
        )
        # creating format with len > 0
        data["format"] = None

        with pytest.raises(ValidationError):
            form = BookAuthorNameForm(data=data)
            form.is_valid()

        data["format"] = "invalid"
        with pytest.raises(ValidationError):
            form = BookAuthorNameForm(data=data)
            form.is_valid()

    def test_clean_is_new_available_negative(self, book_format_form_data):
        form_data, product_category, user, book_author_name, book_format = (
            book_format_form_data()
        )
        # print(f"form data---------------- {form_data}")
        form_data = {
            "is_new_available": -5,  # Invalid value
        }

        assert len(form_data["is_new_available"]) < 0

        with pytest.raises(ValidationError):
            form = BookFormatForm(data=form_data)
            form.is_valid()

    def test_clean_is_used_available_negative():
        form_data = {
            "is_used_available": -10,  # Invalid value
        }
        with pytest.raises(ValidationError):
            form = BookFormatForm(data=form_data)
            form.is_valid()

    def test_clean_publisher_name_required():
        form_data = {
            "publisher_name": "",  # Empty value
        }
        with pytest.raises(ValidationError):
            form = BookFormatForm(data=form_data)
            form.is_valid()

    def test_clean_publishing_date_valid():
        form_data = {
            "publishing_date": date.today(),  # Valid date
        }
        form = BookFormatForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data["publishing_date"] == date.today()

    def test_clean_publishing_date_invalid_format():
        form_data = {
            "publishing_date": "2023-13-01",  # Invalid date format
        }
        with pytest.raises(ValidationError):
            form = BookFormatForm(data=form_data)
            form.is_valid()

    def test_clean_length_negative():
        form_data = {
            "length": -100,  # Invalid negative length
        }
        with pytest.raises(ValidationError):
            form = BookFormatForm(data=form_data)
            form.is_valid()

    def test_clean_narrator_too_long():
        form_data = {
            "narrator": "This is a narrator name that is too long",  # Invalid long narrator name
        }
        with pytest.raises(ValidationError):
            form = BookFormatForm(data=form_data)
            form.is_valid()

    def test_clean_price_too_low_or_None():
        form_data = {
            "price": 0.99,  # Invalid price (too low)
        }
        with pytest.raises(ValidationError):
            form = BookFormatForm(data=form_data)
            form.is_valid()

        form_data = {"price": None}
        with pytest.raises(ValidationError):
            form = BookFormatForm(data=form_data)
            form.is_valid()

    def test_clean_price_too_high():
        form_data = {
            "price": 1000000.00,  # Invalid price (too high)
        }
        with pytest.raises(ValidationError):
            form = BookFormatForm(data=form_data)
            form.is_valid()

    def test_clean_restock_threshold_negative():
        form_data = {
            "restock_threshold": -5,  # Invalid negative threshold
        }
        with pytest.raises(ValidationError):
            form = BookFormatForm(data=form_data)
            form.is_valid()

        form_data = {"restock_threshold": None}  # Invalid negative threshold
        with pytest.raises(ValidationError):
            form = BookFormatForm(data=form_data)
            form.is_valid()

    def test_clean_image_1_required():
        form_data = {
            "image_1": None,  # None value for image_1
        }
        with pytest.raises(ValidationError):
            form = BookFormatForm(data=form_data)
            form.is_valid()

    def test_clean_image_2_required():
        form_data = {
            "image_2": None,  # None value for image_1
        }
        with pytest.raises(ValidationError):
            form = BookFormatForm(data=form_data)
            form.is_valid()

    def test_clean_image_3_required():
        form_data = {
            "image_3": None,  # None value for image_1
        }
        with pytest.raises(ValidationError):
            form = BookFormatForm(data=form_data)
            form.is_valid()


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
        form = ReviewForm(data=data)
        assert form.is_valid()

    def test_review_form_missing_required_field(self, create_image):
        data = {
            "image_1": create_image,
            "image_2": create_image,
            "title": "",
            "content": "I really enjoyed reading this book.",
            "rating": None,
        }
        form = ReviewForm(data=data)
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
