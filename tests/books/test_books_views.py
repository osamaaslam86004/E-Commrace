import pytest
import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from django.test import Client
from django.urls import reverse
from django.contrib.messages import get_messages
from cloudinary.uploader import upload
from book_.models import BookFormat, BookAuthorName
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from tests.books.books_factory_classes import BookAuthorNameFactory, BookFormatFactory
from tests.i.factory_classes import ProductCategoryFactory
from book_.forms import BookAuthorNameForm, BookFormatForm
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def admin_user():
    return CustomUserOnlyFactory(user_type="ADMINISTRATOR")


@pytest.fixture
def build_setup_testing_Bookformat(client):

    def _build_setup_testing_Review(user_type):
        # create a user instance of given type
        user = CustomUserOnlyFactory(user_type=user_type)
        client.force_login(user)

        # Create a Product category for books
        product_category = ProductCategoryFactory(name="BOOKS")

        # Create the bookAuthorName
        book_author_name = BookAuthorNameFactory.build()

        # create BookFormat instance
        book = BookFormatFactory.build(
            user=user,
            book_author_name=book_author_name,
            product_category=product_category,
        )
        return product_category, user, book_author_name, book

    return _build_setup_testing_Review


@pytest.fixture
def create_image(tmpdir):

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
        return form_data

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
        return form_data, user

    return _book_format_form_data


@pytest.mark.django_db
class Test_CreateBookFormatsView:

    @patch("book_.views.upload")
    # @patch("cloudinary.uploader.upload")
    def test_create_book_format_success(
        self,
        mock_upload,
        client,
        book_author_name_form_data,
        book_format_form_data,
        create_image,
    ):
        # Mock the Cloudinary upload response
        mock_upload.side_effect = [
            {"url": "http://example.com/image1.jpg"},
            {"url": "http://example.com/image2.jpg"},
            {"url": "http://example.com/image3.jpg"},
        ]

        book_author_data = book_author_name_form_data()
        book_data, user = book_format_form_data()

        # Ensure the files are part of the request
        files = {
            "image_1": create_image,
            "image_2": create_image,
            "image_3": create_image,
        }

        # assert files is not empty
        # assert all(files.values())

        with patch(
            "book_.views.Create_Book_Formats_View.all_images_uploaded_by_user"
        ) as mock_all_files_uploaded:
            mock_all_files_uploaded.return_value = True

        book_format_form = BookFormatForm(book_data)
        print(f"book format form------------ {book_format_form.errors}")
        assert book_format_form.is_valid()

        book_author_name = BookAuthorNameForm(book_author_data)
        print(f"book author name form------------ {book_author_name.errors}")
        assert book_author_name.is_valid()

        response = client.post(
            reverse("book_:create_update_book_formats"),
            data={**book_author_data, **book_data},
            files=files,
            format="multipart",
        )

        messages = list(get_messages(response.wsgi_request))
        assert any(
            str(message) == "All forms submitted successfully" for message in messages
        )

        assert response.status_code == 301
        assert response.url == reverse("i:success_page")

        book_format = BookFormat.objects.get(user=user)
        assert book_format.image_1 == "http://example.com/image1.jpg"
        assert book_format.image_2 == "http://example.com/image2.jpg"
        assert book_format.image_3 == "http://example.com/image3.jpg"
