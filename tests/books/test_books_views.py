import io
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse
from PIL import Image
from pytest_django.asserts import assertTemplateUsed

from book_.forms import BookAuthorNameForm, BookFormatForm
from book_.models import BookFormat
from tests.books.books_factory_classes import (BookAuthorNameFactory,
                                               BookFormatFactory,
                                               RatingFactory, ReviewFactory)
from tests.Homepage.Homepage_factory import CustomUserOnlyFactory
from tests.i.factory_classes import ProductCategoryFactory


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def admin_user():
    return CustomUserOnlyFactory(user_type="ADMINISTRATOR")


@pytest.fixture
@pytest.mark.django_db
def build_setup_testing_Bookformat(client: Client):

    def _build_setup_testing_Review(user_type):
        # create a user instance of given type
        user = CustomUserOnlyFactory(user_type=user_type)
        assert user is not None

        client.force_login(user)

        session = client.session
        # add user_id to session
        session["user_id"] = user.id
        session.save()

        # Update session's cookie
        from django.conf import settings

        session_cookie_name = settings.SESSION_COOKIE_NAME
        client.cookies[session_cookie_name] = session.session_key

        # Create a Product category for books
        product_category = ProductCategoryFactory(name="BOOKS")
        assert product_category is not None

        # Create the bookAuthorName
        book_author_name = BookAuthorNameFactory.build()
        assert book_author_name is not None

        # create BookFormat instance
        book = BookFormatFactory.build(
            user=user,
            book_author_name=book_author_name,
            product_category=product_category,
        )
        assert book is not None
        assert book.user == user
        assert book.user.user_type == "SELLER"
        assert book.product_category.name == "BOOKS"

        return client, product_category, user, book_author_name, book

    return _build_setup_testing_Review


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


@pytest.fixture
def book_author_name_form_data(build_setup_testing_Bookformat):
    def _book_author_name_form_data():
        client, product_category, user, book_author_name, book_format = (
            build_setup_testing_Bookformat(user_type="SELLER")
        )
        # Form data dictionary
        form_data = {
            "book_name": book_author_name.book_name,
            "author_name": book_author_name.author_name,
            "about_author": book_author_name.about_author,
            "language": book_author_name.language,
        }

        # Check form validation errors
        form = BookAuthorNameForm(data=form_data)

        if not form.is_valid():
            print(f"Form errors: {form.errors}")

        assert form.is_valid(), f"BookAuthorNameForm is not valid: {form.errors}"
        return client, form_data

    return _book_author_name_form_data


@pytest.fixture
def book_format_form_data(build_setup_testing_Bookformat, create_image):
    def _book_format_form_data():
        client, product_category, user, book_author_name, book_format = (
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
            "price": book_format.price,
            "is_active": book_format.is_active,
            "restock_threshold": book_format.restock_threshold,
            "image_1": create_image,
            "image_2": create_image,
            "image_3": create_image,
        }

        files = {
            "image_1": form_data["image_1"],
            "image_2": form_data["image_2"],
            "image_3": form_data["image_3"],
        }
        # Check form validation errors
        form = BookFormatForm(data=form_data, files=files)

        assert form.is_valid(), f"Form is not valid: {form.errors}"

        return client, form_data, user

    return _book_format_form_data


@pytest.mark.django_db
class Test_CreateBookFormatsView:

    @patch("cloudinary.uploader.upload")
    @patch("book_.views.Create_Book_Formats_View.all_images_uploaded_by_user")
    def test_create_book_format(
        self,
        mock_all_images_uploaded_by_user,
        mock_upload,
        book_author_name_form_data,
        book_format_form_data,
    ):

        # Mock the Cloudinary upload response
        cloudinary_mock_response = [
            {"url": "https://example.com/image1.jpg"},
            {"url": "https://example.com/image1.jpg"},
            {"url": "https://example.com/image1.jpg"},
        ]

        mock_upload.side_effect = cloudinary_mock_response

        mock_all_images_uploaded_by_user.return_value = True

        client, book_author_data = book_author_name_form_data()
        print(f"book author data: {book_author_data}")

        client, book_data, user = book_format_form_data()
        print(f"book_data: {book_data}")

        assert client.session["user_id"] == user.id

        files = {
            "image_1": book_data["image_1"],
            "image_2": book_data["image_2"],
            "image_3": book_data["image_3"],
        }

        response = client.post(
            reverse("book_:create_update_book_formats"),
            data={**book_author_data, **book_data},
            files=files,
            enctype="multipart/form-data",
        )

        assert mock_upload.assert_called()

        assert response.status_code == 200

        messages = list(get_messages(response.wsgi_request))
        print(f"Messages: {messages}")

        assert assertTemplateUsed(response, "success_page.html")

        assert BookFormat.objects.filter(user=user).exists()
        book_format = BookFormat.objects.get(user=user)
        assert book_format.image_1 == "http://example.com/image1.jpg"
        assert book_format.image_2 == "http://example.com/image2.jpg"
        assert book_format.image_3 == "http://example.com/image3.jpg"


@pytest.mark.django_db
class Test_DeleteBookFormatIntegration:

    def setup_method(self):
        self.client = Client()

        self.user = CustomUserOnlyFactory(user_type="SELLER")
        assert self.user is not None

        # Create a Product category for books
        product_category = ProductCategoryFactory(name="BOOKS")
        assert product_category is not None

        # Create the bookAuthorName
        self.book_author_name = BookAuthorNameFactory()
        assert self.book_author_name is not None

        # create BookFormat instance
        self.book_format = BookFormatFactory(
            user=self.user,
            book_author_name=self.book_author_name,
            product_category=product_category,
        )
        assert self.book_format is not None

    def test_delete_book_format_integration_success(self):
        """Test successful deletion of a book format."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("book_:delete_book_formats", kwargs={"pk": self.book_format.id})
        )

        # Check for successful redirect
        assert response.status_code == 302
        assert response.url == reverse("i:list_of_books_for_user")

        # Ensure book format is deleted
        with pytest.raises(BookFormat.DoesNotExist):
            BookFormat.objects.get(id=self.book_format.id)

    def test_delete_book_format_integration_permission_denied(self):
        """Test deletion fails for unauthorized user."""
        response = self.client.get(
            reverse("book_:delete_book_formats", kwargs={"pk": self.book_format.id})
        )

        # Ensure user is redirected to login
        assert response.status_code == 302
        assert reverse("Homepage:login") in response.url

    def test_delete_book_format_integration_not_found(self):
        """Test trying to delete a non-existent book format."""
        self.client.force_login(self.user)

        with pytest.raises(BookFormat.DoesNotExist):
            response = self.client.get(
                reverse("book_:delete_book_formats", kwargs={"pk": 999})
            )

            # Check that the response raises 404
            assert response.status_code == 302
            assert response.url == reverse("i:list_of_books_for_user")

            # Check the message about the non-existent book
            messages = list(response.wsgi_request._messages)
            assert len(messages) == 1
            assert (
                str(messages[0]) == "The Book you are trying to delete does not exist."
            )


@pytest.mark.django_db
class Test_FilteredBooksViewIntegration:

    def setup_method(self):
        self.client = Client()
        self.url = reverse("book_:book_list_filters")

        user = CustomUserOnlyFactory(user_type="SELLER")
        assert user is not None
        self.client.force_login(user)

        # Create a Product category for books
        self.product_category = ProductCategoryFactory(name="BOOKS")
        assert self.product_category is not None

        # Setup data for the tests
        author_1 = BookAuthorNameFactory(
            author_name="John Doe", book_name="Python Mastery"
        )
        author_2 = BookAuthorNameFactory(
            author_name="Jane Smith", book_name="Django Basics"
        )

        BookFormatFactory.create_batch(
            3,
            book_author_name=author_1,
            user=user,
            product_category=self.product_category,
            price=20.00,
            is_active=True,
            is_new_available=True,
        )
        BookFormatFactory.create_batch(
            2,
            book_author_name=author_2,
            user=user,
            product_category=self.product_category,
            price=35.00,
            is_active=True,
            is_used_available=True,
        )

        self.book_format_count = BookFormat.objects.all().count()
        assert self.book_format_count == 5

    def test_default_queryset(self):
        """Test that the default queryset (without filters) returns all active book formats."""
        response = self.client.get(self.url)

        assert response.status_code == 200
        content_id = ContentType.objects.get(app_label="book_", model="bookformat").id

        # Verify context variables
        assert response.context["content_id"] == content_id
        assert len(response.context["item_list"]) == 3
        assert response.context["form"] is not None

    def test_filter_by_author_name(self):
        """Test that filtering by author name returns the correct results."""
        response = self.client.get(self.url, {"author_name": "John Doe"})

        assert response.status_code == 200
        books = response.context["item_list"]
        assert len(books) == 3  # Only books by John Doe should be returned

        # Check if all returned books have the correct author
        for book in books:
            assert book.book_author_name.author_name == "John Doe"

    def test_filter_by_price_range(self):
        """Test that filtering by a price range returns the correct results."""
        response = self.client.get(self.url, {"price_min": 25, "price_max": 40})

        assert response.status_code == 200
        books = response.context["item_list"]

        # Expect only books with prices between 25 and 40
        assert len(books) == 2
        for book in books:
            assert 25 <= book.price <= 40

    def test_pagination(self):
        """Test that pagination works correctly."""
        # Set the paginator to display 2 items per page
        response = self.client.get(self.url, {"page": 1})

        assert response.status_code == 200

        page_obj = response.context["item_list"]

        assert len(page_obj.object_list) == 3  # First page contains 3 items
        assert page_obj.has_next()  # There should be more pages

        response = self.client.get(self.url, {"page": 2})
        page_obj = response.context["item_list"]

        assert len(page_obj.object_list) == 2  # Second page contains 2 items
        assert not page_obj.has_next()  # No more pages after this one

    def test_filter_by_multiple_conditions(self):
        """Test filtering with multiple conditions (author name + price + is_new_available)."""
        response = self.client.get(
            self.url,
            {
                "author_name": "John Doe",
                "price_min": 15,
                "price_max": 30,
                "is_new_available": "on",
            },
        )

        assert response.status_code == 200
        books = response.context["item_list"]

        # Check that only the matching books are returned
        assert len(books) == 3
        for book in books:
            assert book.book_author_name.author_name == "John Doe"
            assert 15 <= book.price <= 30
            assert book.is_new_available == 1


@pytest.mark.django_db
class Test_BookDetailView:
    def setup_method(self):
        self.client = Client()

        user = CustomUserOnlyFactory(user_type="SELLER")
        assert user is not None
        self.client.force_login(user)

        # Create a Product category for books
        self.product_category = ProductCategoryFactory(name="BOOKS")
        assert self.product_category is not None

        self.book_author = BookAuthorNameFactory()
        assert self.book_author is not None

        self.book_format = BookFormatFactory(
            book_author_name=self.book_author,
            user=user,
            product_category=self.product_category,
        )
        assert self.book_format is not None

        self.review = ReviewFactory(book_format=self.book_format, user=user)
        assert self.review is not None

        self.rating = RatingFactory(book_format=self.book_format, user=user, rating=4)
        assert self.rating is not None

    def test_view_response(self):
        # URL for the book detail view
        url = reverse(
            "book_:book_detail_view",
            kwargs={"pk": self.book_author.pk, "format_id": self.book_format.id},
        )

        # Make a GET request to the view
        response = self.client.get(url)

        # Check that the response is successful (status code 200)
        assert response.status_code == 200

        # Verify that the correct template is used
        assert "book_detail_view.html" in [t.name for t in response.templates]

        # Check context data for the book details
        assert response.context["book_author_name"] == self.book_author
        assert response.context["book_format"] == self.book_format

        # Check the review_rating_dict in the context
        review_rating_dict = response.context["review_rating_dict"]
        assert self.review in review_rating_dict
        assert (
            review_rating_dict[self.review].rating == 4
        )  # Assuming a rating of 4 for the test

        # Check total ratings and average rating calculations
        assert (
            response.context["total_ratings"] == 1
        )  # Because we added only one rating
        assert response.context["average_rating"] == 4.0  # Rating set as 4

    def test_star_ratings_calculations(self):
        url = reverse(
            "book_:book_detail_view",
            kwargs={"pk": self.book_author.pk, "format_id": self.book_format.id},
        )
        response = self.client.get(url)

        star_ratings = response.context["star_ratings"]
        width_percentages = response.context["width_percentages"]

        # Validate star ratings logic
        assert star_ratings[5] == 0  # Assuming no 5-star ratings
        assert star_ratings[4] == 1  # One 4-star rating
        assert star_ratings[3] == 0
        assert star_ratings[2] == 0
        assert star_ratings[1] == 0

        # Validate width percentage calculation (since only 1 rating)
        assert width_percentages[4] == 100  # Only 1 rating out of 1, so it's 100%
        assert width_percentages[5] == 0
        assert width_percentages[3] == 0

    def test_product_browsing_history(self):
        url = reverse(
            "book_:book_detail_view",
            kwargs={"pk": self.book_author.pk, "format_id": self.book_format.id},
        )
        response = self.client.get(url)

        # Check that the browsing history is updated correctly
        zipped_history = response.context["zipped"]
        assert len(zipped_history) == 1  # Ensure one item added to browsing history

        product_details = zipped_history[0]  # Assuming this is a tuple
        print(f"product details: {product_details}")
        (
            product_name,
            product_price,
            product_rating,
            product_image_url,
            path,
            special_features,
        ) = product_details

        assert product_name == self.book_format.book_author_name.book_name
        assert product_price == str(self.book_format.price)
        assert product_rating == Decimal(4.0)
        assert product_image_url == str(self.book_format.image_1)
        assert path == "http://testserver" + url
        assert special_features == [1]
