import io
import json
import logging
import random
from base64 import urlsafe_b64encode
from typing import Any, Dict
from unittest.mock import Mock, patch
from urllib.parse import urlencode

import pytest
import requests_mock
from celery.exceptions import MaxRetriesExceededError
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages import get_messages
from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.response import TemplateResponse
from django.test import Client, RequestFactory
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from faker import Faker
from PIL import Image
from pytest_django.fixtures import SettingsWrapper

from Homepage.forms import (
    AdministratorProfileForm,
    CustomerProfileForm,
    CustomerServiceProfile,
    CustomerServiceProfileForm,
    CustomUserImageForm,
    E_MailForm_For_Password_Reset,
    LogInForm,
    ManagerProfile,
    ManagerProfileForm,
    OTPForm,
    SellerProfileForm,
    SignUpForm,
    UserProfileForm,
)
from Homepage.models import (
    AdministratorProfile,
    CustomerProfile,
    CustomerServiceProfile,
    CustomSocialAccount,
    CustomUser,
    ManagerProfile,
    SellerProfile,
    UserProfile,
)
from Homepage.tasks import send_password_reset_email
from Homepage.views import (
    CustomerProfilePageView,
    CustomLoginView,
    CustomPasswordResetConfirmView,
    HomePageView,
    Payment,
)
from tests.Homepage.Custom_Permissions import (
    ADMIN_CUSTOM_PERMISSIONS,
    CSR_CUSTOM_PERMISSIONS,
    CUSTOMER_CUSTOM_PERMISSIONS,
    MANAGER_CUSTOM_PERMISSIONS,
    SELLER_CUSTOM_PERMISSIONS,
)
from tests.Homepage.Homepage_factory import (
    CustomerProfileFactory,
    CustomUserFactory,
    CustomUserOnlyFactory,
)

fake = Faker()


# Disable Faker DEBUG logging
faker_logger = logging.getLogger("faker")
faker_logger.setLevel(logging.WARNING)


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def otp_form_data():
    """Fixture to generate form data for OTPForm."""
    otp = fake.random_int(min=100000, max=999999)  # Generate a 6-digit OTP
    return {"otp": otp}


@pytest.fixture
def custom_user():
    def _custom_user():
        user = CustomUserFactory()

        # Create a UserProfile for the user
        user_profile = UserProfile.objects.create(
            user=user,
            full_name="",
            age=18,
            gender="",
            phone_number="",
            city="",
            country="",
            postal_code="",
        )
        return user, user_profile

    return _custom_user


@pytest.fixture
def signup_form_data():
    user = CustomUserFactory.build()
    return {
        "username": user.username,
        "email": user.email,
        "user_type": user.user_type,
        "password1": "testpass123",
        "password2": "testpass123",
    }


@pytest.fixture
def login_form_data():
    def _login_form_data(user):
        return {
            "email": user.email,
            "password": "testpass123",
        }

    return _login_form_data


@pytest.fixture
def invalid_form_data():
    return {
        "email": "invalid@example.com",
        "password": "wrongpassword",
    }


@pytest.fixture
def create_social_account():
    def make_social_account(user):
        return CustomSocialAccount.objects.create(
            user=user,
            access_token="fake_token",
            user_info="fake_info",
            code="fake_code",
            refresh_token="fake_refresh_token",
        )

    return make_social_account


@pytest.fixture
def client_logged_in_with_social_account(client, custom_user, create_social_account):
    # Create user and social account
    user, _ = custom_user()
    social_account = create_social_account(user)

    client.force_login(user)

    # Log-in the user with social account
    session = client.session
    session["user_id"] = user.id
    session.save()

    return client, user, social_account


@pytest.fixture
def client_logged_in(client, custom_user, login_form_data):
    # Create user
    user, _ = custom_user()

    # Log-in the user
    response = client.post(reverse("Homepage:login"), login_form_data(user))

    # Create the session for the user
    session = client.session
    session["user_id"] = user.id
    session.save()

    assert response.status_code == 302
    assert response.url == "/"
    assert "user_id" in client.session

    return response.client, user


@pytest.fixture
def group_user_logged_in(client, login_form_data):
    def _client_logged_in(user):

        # Log-in the user
        response = client.post(reverse("Homepage:login"), login_form_data(user))

        # Create the session for the user
        session = client.session
        session["user_id"] = user.id
        session.save()

        # Update session's cookie
        session_cookie_name = settings.SESSION_COOKIE_NAME
        client.cookies[session_cookie_name] = session.session_key

        assert response.status_code == 302
        assert response.url == "/"
        assert "user_id" in client.session

        return response.client

    return _client_logged_in


@pytest.fixture
def mock_payment():
    payment = Payment.objects.create(stripe_customer_id="stripe_customer_id_here")
    return payment


@pytest.fixture
def password_reset_form_data():
    return {
        "new_password1": "new_secure_password",
        "new_password2": "new_secure_password",
    }


@pytest.fixture
def password_reset_invalid_form_data():
    return {
        "new_password1": "secure_password",
        "new_password2": "new_secure_password",
    }


@pytest.fixture
def uid_and_token(custom_user):
    user, _ = custom_user()
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uidb64, token


@pytest.fixture
def user_profile_form_data(faker):

    # Randomly select a country code for realistic data generation
    countries = ["CA", "NZ"]
    chosen_country = random.choice(countries)

    from phonenumbers import PhoneNumberFormat, format_number, parse

    number = parse("6044011234", "CA")
    formatted_number = format_number(number, PhoneNumberFormat.INTERNATIONAL)

    # Generate a postal code with exactly 20 characters
    postal_code = faker.bothify(text="?" * 20)

    return {
        "full_name": faker.name(),
        "age": faker.random_int(min=18, max=130),
        "gender": faker.random_element(
            elements=["Male", "Female", "Non-binary", "Other"]
        ),
        "phone_number": formatted_number,
        "city": faker.city(),
        "country": chosen_country,
        "postal_code": postal_code,
        "shipping_address": faker.address(),
    }


@pytest.fixture
def customer_profile_form_data(faker):
    return {
        "shipping_address": faker.address(),
        "wishlist": faker.random_int(min=1, max=50),
    }


@pytest.fixture
def seller_profile_form_data(faker):
    # Generate address-like text with at most 100 characters
    address = faker.text(max_nb_chars=100)
    return {"address": address}


@pytest.fixture
def customer_service_profile_form_data(faker):
    # Generate form data that respects model field constraintsf
    return {
        "department": faker.job()[:50],  # Job title, truncated to 50 characters
        "bio": faker.text(max_nb_chars=100),  # Bio, limited to 500 characters
        "experience_years": faker.random_int(min=1, max=40),
    }


@pytest.fixture
def manager_profile_form_data(faker):
    # Generate form data that respects model field constraints
    return {
        "team": faker.text(max_nb_chars=50),
        "reports": faker.text(max_nb_chars=100),
        "bio": faker.text(max_nb_chars=100),
        "experience_years": faker.random_int(min=1, max=40),
    }


@pytest.fixture
def admin_profile_form_data(faker):
    # Generate form data that respects model field constraints
    return {
        "bio": faker.text(max_nb_chars=100),  # Bio, limited to 500 characters
        "experience_years": faker.random_int(min=1, max=40),
    }


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

    # Create the form data
    data = {}
    file_dict = {"image": uploaded_file}
    return file_dict


@pytest.mark.django_db
class Test_HomePageView:
    def test_homepage_view(client: Client):
        # Mock Cloudinary image URLs
        cloudinary_images = {
            "box_7": "https://example.com/box_7.jpg",
            "box_6": "https://example.com/box_6.jpg",
            "box_5": "https://example.com/box_5.jpg",
            "box_3": "https://example.com/box_3.jpg",
            "box_8": "https://example.com/box_8.jpg",
            "box_2": "https://example.com/box_2.jpg",
            "box_1": "https://example.com/box_1.jpg",
            "U_N": "https://example.com/U_N.jpg",
            "ama_zon_logo": "https://example.com/ama_zon_logo.jpg",
            "cart_50_50": "https://example.com/cart_50_50.jpg",
        }

        # Mock Cloudinary's build_url method
        def mock_build_url(name):
            mock_image = Mock()
            mock_image.build_url.return_value = cloudinary_images[name]
            return mock_image

        with patch(
            "Homepage.views.cloudinary.CloudinaryImage", side_effect=mock_build_url
        ):
            # Create a request factory instance
            factory = RequestFactory()
            request = factory.get(
                reverse("Homepage:Home")
            )  # Adjust the URL name as per your project

            # Mock the session
            request.session = {}

            # Create an instance of the view and call get_context_data
            view = HomePageView()
            view.setup(request)
            context = view.get_context_data()

            # Assert that the context contains the expected data
            assert context["images"] == [
                "https://example.com/box_7.jpg",
                "https://example.com/box_6.jpg",
                "https://example.com/box_5.jpg",
                "https://example.com/box_3.jpg",
                "https://example.com/box_8.jpg",
                "https://example.com/box_2.jpg",
                "https://example.com/box_1.jpg",
                "https://example.com/U_N.jpg",
                "https://example.com/ama_zon_logo.jpg",
            ]
            assert context["cart_url"] == "https://example.com/cart_50_50.jpg"
            assert (
                "zipped" in context
            )  # Assuming your_browsing_history returns something non-empty


@pytest.mark.django_db
class Test_SignupView:

    def test_signup_view_get(self, client: Client):
        # Ensure the client is logged out (if necessary)
        client.logout()

        # Perform GET request to signup endpoint
        response = client.get(reverse("Homepage:signup"))

        # Assert the response status code is 200 OK
        assert response.status_code == 200

        # Assert that the 'form' key is in the response context
        assert "form" in response.context

        # Assert that the form in the context is an instance of SignUpForm
        assert isinstance(response.context["form"], SignUpForm)

    def test_signup_view_post_success(
        self, client: Client, signup_form_data: dict[str, Any]
    ):
        # Ensure the client is logged out
        client.logout()
        response = client.post(reverse("Homepage:signup"), signup_form_data)
        assert response.status_code == 302

        assert response.url == reverse("Homepage:login")

        # Verify user creation
        user = CustomUser.objects.filter(email=signup_form_data["email"]).first()
        assert user is not None
        assert user.username == signup_form_data["username"]

    def test_signup_view_existing_user(self, client: Client, signup_form_data):
        # Create a user with the same email
        CustomUser.objects.create(
            username=signup_form_data["username"],
            email=signup_form_data["email"],
            password=signup_form_data["password1"],
        )

        # Ensure the client is logged out
        client.logout()

        response = client.post(reverse("Homepage:signup"), signup_form_data)
        assert response.status_code == 302  # 200 OK
        assert response.url == reverse("Homepage:signup")

        # Check for error message in response context
        # Access messages from the response
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) > 0
        assert any(
            "A user with the email already exists" in str(message)
            for message in messages
        )


@pytest.mark.django_db
class Test_CustomLoginView:

    def test_get_authenticated_user(self, client, custom_user):
        user, profile = custom_user()
        client.force_login(user)
        response = client.get(reverse("Homepage:login"))
        assert user.is_authenticated
        assert response.status_code == 302
        assert response.url == "/"

    def test_get_anonymous_user(self, client):
        response = client.get(reverse("Homepage:login"))
        assert response.status_code == 200
        assert "form" in response.context
        assert isinstance(response.context["form"], LogInForm)

    def test_post_successful_login(self, client, custom_user, login_form_data):
        client.logout()

        user, profile = custom_user()
        response = client.post(reverse("Homepage:login"), login_form_data(user))

        session = client.session
        session["user_id"] = user.id
        session.save()

        assert response.status_code == 302
        assert response.url == "/"
        assert "user_id" in client.session

        messages = list(response.wsgi_request._messages)
        assert any("Successfully Logged In" in str(message) for message in messages)

    def test_post_invalid_credentials(self, client, invalid_form_data):
        response = client.post(reverse("Homepage:login"), invalid_form_data)
        assert response.status_code == 302
        assert response.url == reverse("Homepage:signup")

        messages = list(response.wsgi_request._messages)
        assert any(
            "User not found: Invalid credentials" in str(message)
            for message in messages
        )

    def test_post_invalid_form(self, client):
        response = client.post(reverse("Homepage:login"), {})
        assert response.status_code == 200
        assert "form" in response.context
        assert isinstance(response.context["form"], LogInForm)

        messages = list(response.wsgi_request._messages)
        assert any("This field is required." in str(message) for message in messages)

    def test_start_cookie_session(self, client, custom_user):
        # Simulate the creation of sessionid cookie
        user, profile = custom_user()
        client.force_login(user)
        session = client.session
        session["user_id"] = user.id
        session.save()

        assert session["user_id"] == user.id

    def test_check_existing_cookie_session(self, client, custom_user):
        # Create the user instance
        user, profile = custom_user()

        # Create the sessionid cookie
        client.force_login(user)
        session = client.session
        session["user_id"] = user.id
        session.save()

        # Calling the View to confirm sessionid cookie already exist
        response = client.get(reverse("Homepage:login"))
        assert response.url == "/"
        messages = list(response.wsgi_request._messages)
        assert any("You are already logged in." in str(message) for message in messages)

    def test_check_non_existing_cookie_session(self, client):
        client.logout()

        view = CustomLoginView()
        request = client.request().wsgi_request
        view.setup(request)
        assert view.check_existing_cookie_session(request) is False


@pytest.mark.django_db
class TestCustomLogoutView:
    def test_logout_success(self, client_logged_in):
        client, user = client_logged_in

        # Perform GET request to logout endpoint
        response = client.get(reverse("Homepage:logout"))
        messages = list(get_messages(response.wsgi_request))
        assert "sessionid" not in client.session

        assert response.status_code == 302
        assert response.url == reverse("Homepage:login")
        assert any(
            "You have been logged out successfully" in str(message)
            for message in messages
        )

    def test_logout_with_social_account(
        self, create_social_account, custom_user, client
    ):
        # create a user instance for Social Account
        user, _ = custom_user()

        # Create a Social Account
        social_account = create_social_account(user)

        client.force_login(user)

        with requests_mock.Mocker() as mock:
            # Mock the POST request to Google's token revoke endpoint
            mock.post("https://oauth2.googleapis.com/revoke", status_code=200)

            response = client.get(reverse("Homepage:logout"))
            messages = list(get_messages(response.wsgi_request))

            assert response.status_code == 302
            assert response.url == reverse("Homepage:login")
            # assert any(
            #     "You have been logged out successfully" in str(message)
            #     for message in messages
            # )
            assert social_account.access_token is not None
            assert social_account.refresh_token is not None

    # def test_logout_social_account_google_fail(
    #     self, create_social_account, custom_user, client
    # ):
    #     # create a user instance for Social Account
    #     user, _ = custom_user()

    #     # Create a Social Account
    #     social_account = create_social_account(user)
    #     client.force_login(user)

    #     session = client.session
    #     session["user_id"] = user.id
    #     session["social_id"] = user.id
    #     session.save()

    #     assert "user_id" in session

    #     with requests_mock.Mocker() as mock:
    #         mock.post(
    #             "https://oauth2.googleapis.com/revoke",
    #             exc=requests.exceptions.RequestException,
    #         )

    #         response = client.get(reverse("Homepage:logout"))
    #         messages = list(get_messages(response.wsgi_request))
    #         social_account.refresh_from_db()

    #         assert response.status_code == 302
    #         assert response.url == reverse("Homepage:login")

    #     assert social_account.access_token == ""

    def test_logout_no_user_id_in_session(self, client_logged_in):

        # Simulate sessionid cookie not in web browser / user_id not in session cookie
        client, user = client_logged_in
        response = client.get(reverse("Homepage:logout"))
        messages = list(get_messages(response.wsgi_request))

        assert response.status_code == 302
        assert response.url == reverse("Homepage:login")
        assert any(
            "You have been logged out successfully" in str(message)
            for message in messages
        )
        assert "sessionid" not in response.wsgi_request.session

    def test_logout_anonymous_user(self, client):
        response = client.get(reverse("Homepage:logout"))
        messages = list(get_messages(response.wsgi_request))

        assert response.status_code == 302
        assert response.url == reverse("Homepage:login")
        assert any(
            "You are not logged in. Please login!" in str(message)
            for message in messages
        )


@pytest.mark.django_db
class Test_DeleteUserAccountView:

    @patch("stripe.Customer.delete")
    def test_delete_user_account_authenticated(
        self, mock_stripe_customer_delete, client_logged_in
    ):
        client, user = client_logged_in

        mock_stripe_customer_delete.return_value = {"deleted": True}

        # Create a payment instance for user
        Payment.objects.create(user=user)
        # Mock the delete method of CustomUser to avoid actual deletion
        with patch.object(CustomUser, "delete") as mock_delete:
            response = client.get(reverse("Homepage:delete"))

        assert response.status_code == 302  # Redirects to Homepage:Home
        assert mock_stripe_customer_delete.called
        assert mock_delete.called

        # Check messages set in the response
        storage = get_messages(response.wsgi_request)
        assert any(msg.message == "Your account is deleted!" for msg in storage)

    @patch("stripe.Customer.delete")
    def test_delete_user_account_not_authenticated(
        self, mock_stripe_customer_delete, client
    ):

        mock_stripe_customer_delete.return_value = {"deleted": True}
        url = reverse("Homepage:delete")
        # No user session set
        response = client.get(url)

        assert response.status_code == 302  # Redirects to Homepage:login
        assert not mock_stripe_customer_delete.called

    @patch("stripe.Customer.delete")
    def test_delete_user_account_no_payment(
        self, mock_stripe_customer_delete, client_logged_in
    ):

        mock_stripe_customer_delete.return_value = {"deleted": True}
        # create user, log-in the user
        client, user = client_logged_in
        # Simulate no payments associated with the user
        with patch.object(Payment.objects, "filter", return_value=[]):
            response = client.get(reverse("Homepage:delete"))

        assert response.status_code == 302
        assert not mock_stripe_customer_delete.called
        assert not CustomUser.objects.filter(id=user.id).exists()

    # @pytest.mark.django_db
    # def test_delete_user_account_no_payment_with_social_account(
    #     self, client_logged_in_with_social_account
    # ):
    #     # Create user, log-in the user with social account
    #     client, user, social_account = client_logged_in_with_social_account

    #     id = user.id
    #     social_id = CustomSocialAccount.objects.get(user__id=id)

    #     response = client.get(reverse("Homepage:delete"))

    #     assert response.status_code == 302

    #     assert not "sessionid" in response.client.cookies

    #     # Verify that the user is deleted
    #     assert not CustomUser.objects.filter(id=id).exists()
    #     # Verify that the social account is deleted
    #     assert not CustomSocialAccount.objects.filter(id=social_id).exists()


@pytest.mark.django_db
class Test_GoogleLogin:
    def test_google_login(self, client: Client, settings: SettingsWrapper):
        # Setup the necessary settings for Google OAuth
        settings.GOOGLE_OAUTH_CLIENT_ID = "test-client-id"
        settings.GOOGLE_OAUTH_REDIRECT_URI = "http://localhost:8000/oauth2/callback"

        # Make a GET request to the view
        response = client.get(reverse("Homepage:google_login"))

        # Prepare the expected redirect URL
        params = {
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
            "scope": "email https://www.googleapis.com/auth/drive.readonly",
            "response_type": "code",
            "access_type": "offline",
        }
        expected_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"

        # Check if the response is a redirect to the expected URL
        assert response.status_code == 302
        assert response["Location"] == expected_url


@pytest.mark.django_db
class Test_GoogleOAuthCallback:

    @patch("requests.post")
    @patch("requests.get")
    def test_google_callback_new_user(
        self, mock_get, mock_post, settings: SettingsWrapper, client: Client
    ):
        # Set up the necessary settings for Google OAuth
        settings.GOOGLE_OAUTH_CLIENT_ID = "test-client-id"
        settings.GOOGLE_OAUTH_CLIENT_SECRET = "test-client-secret"
        settings.GOOGLE_OAUTH_REDIRECT_URI = "/"

        # Mock the response for token exchange
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
        }

        # Mock the response for user info
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"email": "testuser@example.com"}

        # Making sure user with the email does not exist
        assert not CustomUser.objects.filter(email="testuser@example.com").exists()

        # # Simulate the callback with the authorization code
        response = client.get(
            reverse("Homepage:your_callback_view"), {"code": "test-code"}
        )

        # # Check that the response is a redirect to the home page
        assert response.status_code == 302
        assert response.url == reverse("Homepage:Home")

        # # Get the user to make sure a new User is created
        user = CustomUser.objects.get(email="testuser@example.com")
        assert user is not None

        # Check that the social account is created
        social_account = CustomSocialAccount.objects.get(user=user)
        assert social_account.access_token == "test-access-token"

        # Check that the user is logged in
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert str(messages[0]) == "Welcome! you are logged-in"

    @patch("requests.post")
    @patch("requests.get")
    def test_google_callback_existing_user(self, mock_get, mock_post, client, settings):

        user = CustomUserOnlyFactory.create(
            email="testuser@example.com", user_type="SELLER", user_google_id=123456
        )

        user = CustomUser.objects.filter(email="testuser@example.com")
        assert user.count() == 1

        user = CustomUser.objects.get(email="testuser@example.com")
        assert not CustomSocialAccount.objects.filter(user=user).exists()

        # Create an existing social account for the user
        social_account = CustomSocialAccount.objects.create(
            user=user,
            access_token="old-access-token",
            user_info={},
            refresh_token="old-refresh-token",
            code={},
        )
        assert CustomSocialAccount.objects.filter(user=user).exists()
        # Verify initial state
        assert social_account.access_token == "old-access-token"

        # Mock the response for token exchange
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
        }

        # Mock the response for user info
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"email": "testuser@example.com"}

        # Set up the necessary settings for Google OAuth
        settings.GOOGLE_OAUTH_CLIENT_ID = "test-client-id"
        settings.GOOGLE_OAUTH_CLIENT_SECRET = "test-client-secret"
        settings.GOOGLE_OAUTH_REDIRECT_URI = "http://localhost:8000/oauth2/callback"

        # Simulate the callback with the authorization code
        response = client.get(
            reverse("Homepage:your_callback_view"), {"code": "test-code"}
        )

        # Check that the response is a redirect to the home page
        assert response.status_code == 302

        # Refresh the social_account from the database
        social_account.refresh_from_db()

        # Check that the user's social account is updated with tokens
        assert social_account.access_token == "test-access-token"
        assert social_account.refresh_token == "test-refresh-token"

        # Check that the user is logged in
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert str(messages[0]) == "Welcome! you are logged-in"


@pytest.mark.django_db
class Test_PasswordReset:

    @pytest.mark.usefixtures("celery_session_app")
    @pytest.mark.usefixtures("celery_session_worker")
    @patch("Homepage.tasks.SendGridAPIClient.send")
    def test_send_password_reset_email_success(self, mock_send):
        # Arrange
        mock_send.return_value.status_code = 202  # Simulate a successful email send
        email = "test@example.com"
        reset_url = "http://example.com/reset?uid=123&token=abc"

        # Act
        result = send_password_reset_email.delay(email, reset_url)
        assert result.get(timeout=30) is None  # Increase timeout to 30 seconds

        # Assert
        assert result.successful()  # Check if the task was successful
        assert mock_send.called

    @pytest.mark.usefixtures("celery_session_app")
    @pytest.mark.usefixtures("celery_session_worker")
    @patch("Homepage.tasks.SendGridAPIClient.send")
    def test_send_password_reset_email_retries(self, mock_send):
        # Arrange
        mock_send.side_effect = [
            Exception("Failed to send email"),
            Exception("Failed to send email"),
            Exception("Failed to send email"),
        ]
        email = "test@example.com"
        reset_url = "http://example.com/reset?uid=123&token=abc"

        with pytest.raises(MaxRetriesExceededError):
            # Act
            result = send_password_reset_email.delay(email, reset_url)
            # Assert
            assert result.get()

        assert mock_send.call_count == 4

    @patch("Homepage.tasks.send_password_reset_email.delay")
    def test_custom_password_reset_existing_user(
        self, mock_send_password_reset_email_delay, client: Client
    ):
        # Create a test user
        user = CustomUser.objects.create(email="test@example.com")

        # Test the GET request
        response = client.get(reverse("Homepage:password_reset"))
        assert response.status_code == 200
        assert "form" in response.context

        # Set up the mock to return a successful response
        mock_send_password_reset_email_delay.return_value = Mock(status_code=202)

        # Test the POST request with a valid email
        response = client.post(
            reverse("Homepage:password_reset"), {"email": "test@example.com"}
        )
        assert response.status_code == 302
        mock_send_password_reset_email_delay.called
        assert response.url == reverse("Homepage:password_reset_done")

        # Test the password reset confirmation
        uid = urlsafe_b64encode(force_bytes(user.pk)).decode()
        token = default_token_generator.make_token(user)
        response = client.get(
            reverse(
                "Homepage:password_reset_confirm",
                kwargs={"uidb64": uid, "token": token},
            )
        )
        assert response.status_code == 200

    def test_password_reset_non_existing_user(self, client, settings):
        # Set up the necessary settings for SendGrid
        settings.SENDGRID_API_KEY = "test-api-key"
        settings.CLIENT_EMAIL = "client@example.com"

        # Make a POST request to the password reset view with a non-existing email
        response = client.post(
            reverse("Homepage:password_reset"),
            {"email": "nonexisting@example.com"},
        )

        # Check the response status code
        assert response.status_code == 302
        assert response.url == reverse("Homepage:signup")

        # Check that no email was sent
        assert len(mail.outbox) == 0

        # Check that the error message is displayed
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert str(messages[0]) == "No user found with this email."


@pytest.mark.django_db
class Test_CustomPasswordResetConfirmView:
    def test_get_valid_link(self, client: Client, custom_user):
        user, _ = custom_user()

        uid = urlsafe_b64encode(force_bytes(user.pk)).decode()
        token = default_token_generator.make_token(user)

        with patch("django.utils.encoding.force_str", return_value=str(user.pk)):
            with patch(
                "django.utils.http.urlsafe_base64_decode",
                return_value=force_bytes(user.pk),
            ):
                url = reverse(
                    "Homepage:password_reset_confirm",
                    kwargs={"uidb64": uid, "token": token},
                )
                response = client.get(url, follow=True)  # Follow the redirect
                assert response.status_code == 200
                assert "validlink" in response.context
                assert response.context["validlink"] is True

    def test_get_invalid_link(self, client, custom_user):
        user, _ = custom_user()

        uid = urlsafe_b64encode(force_bytes(user.pk)).decode()
        token = default_token_generator.make_token(user)

        with patch("django.utils.encoding.force_str", return_value=str(user.pk)):
            with patch(
                "django.utils.http.urlsafe_base64_decode",
                return_value=force_bytes(user.pk),
            ):
                url = reverse(
                    "Homepage:password_reset_confirm",
                    kwargs={"uidb64": uid, "token": "invalid_token"},
                )
                response = client.get(url)
                assert response.status_code == 302
                assert response.url == reverse("Homepage:signup")

                messages = list(get_messages(response.wsgi_request))
                assert len(messages) == 1
                assert str(messages[0]) == "The URL you recieved in e-mail is not valid"

    def test_post_valid_data(self, client: Client, custom_user):

        user, _ = custom_user()
        # Generate a token for the user
        token = default_token_generator.make_token(user)
        # Encode the user's primary key to be used in the URL
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        # Prepare valid form data
        form_data = {
            "new_password1": "Newpassword1122334455_!",
            "new_password2": "Newpassword1122334455_!",
        }

        from Homepage.forms import CustomPasswordResetForm

        form = CustomPasswordResetForm(data=form_data)
        assert form.is_valid()

        url = reverse(
            "Homepage:password_reset_confirm",
            kwargs={"uidb64": uidb64, "token": token},
        )

        response = client.post(url, data=form_data)
        assert response.url == reverse("Homepage:password_reset_complete")

        # Assert no error messages are set
        # messages = list(get_messages(response.wsgi_request))
        # assert ["Password Reset Complete!"] == [message.message for message in messages]

        # Assert that the user's password has been updated
        user.refresh_from_db()
        assert user.check_password(form_data["new_password1"])

    def test_post_invalid_data(
        self, client, uid_and_token, password_reset_invalid_form_data
    ):
        uid, token = uid_and_token
        url = reverse(
            "Homepage:password_reset_confirm",
            kwargs={"uidb64": uid, "token": token},
        )
        response = client.post(url, password_reset_invalid_form_data)
        assert response.status_code == 200
        assert "form" in response.context


@pytest.mark.django_db
class Test_CustomerProfilePageViewGet:
    def test_get_authenticated(self, client: Client):

        user = CustomUser.objects.create(
            email="testuser@example.com",
            username="testuser",
            password="Testpass123!",
            user_type="CUSTOMER",
        )

        customer_profile = UserProfile.objects.create(user=user)
        CustomerProfile.objects.create(
            customer_profile=customer_profile, customuser_type_1=user, wishlist=10
        )
        client.force_login(user)
        session = client.session
        session["user_id"] = user.id
        session.save()

        # Update session's cookie
        session_cookie_name = settings.SESSION_COOKIE_NAME
        client.cookies[session_cookie_name] = session.session_key

        response = client.get(reverse("Homepage:customer_profile_page"))

        assert response.status_code == 200
        assert isinstance(response, TemplateResponse)
        assert "customer_profile_page.html" in [t.name for t in response.templates]
        assert "user_id" in response.wsgi_request.session

    def test_get_not_authenticated(self, client, custom_user):
        user, _ = custom_user()
        response = client.get(reverse("Homepage:customer_profile_page"))

        assert response.status_code == 302
        assert response.url == "/login/?next=/customer_profile_page/"

    def test_handle_no_permission(self, client):
        # Created a user with invald user type
        user = CustomUserOnlyFactory(
            username="testuser",
            email="testuser@gmail.com",
            password="pass123",
            user_type="SELLER",
        )
        client.force_login(user)

        response = client.get(reverse("Homepage:customer_profile_page"))

        assert response.status_code == 200
        assert "permission_denied.html" in [t.name for t in response.templates]

        user = CustomUser.objects.get(email="testuser@gmail.com", user_type="SELLER")

        pre_defined_user_permissions = user.get_all_permissions()

        assert len(SELLER_CUSTOM_PERMISSIONS) == len(pre_defined_user_permissions)

    def test_form_rendering(self, client: Client):
        # Created a user with invald user type
        user = CustomUser.objects.create(
            email="testuser@example.com",
            username="testuser",
            password="Testpass123!",
            user_type="CUSTOMER",
        )

        customer_profile = UserProfile.objects.create(user=user)
        CustomerProfile.objects.create(
            customer_profile=customer_profile, customuser_type_1=user, wishlist=10
        )
        client.force_login(user)
        session = client.session
        session["user_id"] = user.id
        session.save()

        # Update session's cookie
        session_cookie_name = settings.SESSION_COOKIE_NAME
        client.cookies[session_cookie_name] = session.session_key

        response = client.get(reverse("Homepage:customer_profile_page"))
        assert response.status_code == 200
        # Check that all necessary forms are present in the context
        assert "user_profile_form" in response.context
        assert "customer_profile_form" in response.context
        assert "image_form" in response.context

    def test_image_upload(self):

        # Create an image file using Pillow
        image = Image.new("RGB", (100, 100), color="red")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        # Create a SimpleUploadedFile from the image bytes
        uploaded_file = SimpleUploadedFile(
            "test_image.jpg", image_bytes.read(), content_type="image/jpeg"
        )

        # Create the form data
        data = {}
        file_dict = {"image": uploaded_file}
        form = CustomUserImageForm(data, file_dict)

        # Print the form errors for debugging
        print(f"Form errors: {form.errors}")

        # Assert that the form is valid
        assert form.is_valid()

    @patch("Homepage.views.upload")
    @patch("Homepage.views.UserProfileForm")
    @patch("Homepage.views.CustomerProfileForm")
    @patch("Homepage.views.CustomUserImageForm")
    def test_customer_successful_profile_update(
        self,
        mock_image_form,
        mock_customer_profile_form,
        mock_user_profile_form,
        mock_upload,
        client: Client,
        user_profile_form_data,
        customer_profile_form_data,
        create_image,
    ):
        # Configure the mock to return a successful response
        mock_upload.return_value = {"url": "http://example.com/test_image.jpg"}

        user = CustomUser.objects.create(
            email="testuser@example.com",
            username="testuser",
            user_type="CUSTOMER",
        )

        customer_profile = UserProfile.objects.create(user=user)
        CustomerProfile.objects.create(
            customer_profile=customer_profile, customuser_type_1=user, wishlist=10
        )

        client.force_login(user)
        session = client.session
        session["user_id"] = user.id
        session.save()

        # Update session's cookie
        session_cookie_name = settings.SESSION_COOKIE_NAME
        client.cookies[session_cookie_name] = session.session_key

        mock_user_profile_form.return_value.is_valid.return_value = True
        mock_user_profile_form_instance = mock_user_profile_form.return_value
        mock_user_profile_form_instance.save.return_value = Mock()

        mock_customer_profile_form_instance = mock_customer_profile_form.return_value
        mock_customer_profile_form_instance.is_valid.return_value = True
        mock_customer_profile_form_instance.save.return_value = Mock()

        mock_image_form_instance = mock_image_form.return_value
        mock_image_form_instance.is_valid.return_value = True
        mock_image_form_instance.save.return_value = Mock()

        userprofileform = UserProfileForm(data=user_profile_form_data)
        print(f"form errors: {userprofileform.errors}")
        assert userprofileform.is_valid()

        assert CustomerProfileForm(customer_profile_form_data).is_valid()

        file_dic = create_image

        from Homepage.forms import CustomUserImageForm

        image_form = CustomUserImageForm({"image": file_dic["image"]})
        assert image_form.is_valid()

        data = {
            **user_profile_form_data,
            **customer_profile_form_data,
            "image": file_dic["image"],
        }

        response = client.post(
            reverse("Homepage:customer_profile_page"),
            data=data,
            files=file_dic,
        )

        assert response.status_code == 302
        assert user.image, "http://example.com/test_image.jpg"
        assert response.url == "/"


@pytest.mark.django_db
class Test_SellerProfilePageViewGet:
    def test_get_authenticated(self, group_user_logged_in):
        user = CustomUserFactory(
            username="testuser", user_type="SELLER", email="testuser@gmail.com"
        )
        client = group_user_logged_in(user)
        response = client.get(reverse("Homepage:seller_profile_page"))

        assert response.status_code == 200
        assert isinstance(response, TemplateResponse)
        assert "seller_profile_page.html" in [t.name for t in response.templates]
        assert "user_id" in response.wsgi_request.session

    def test_get_not_authenticated(self, client, custom_user):
        user, _ = custom_user()
        response = client.get(reverse("Homepage:seller_profile_page"))

        assert response.status_code == 302
        assert response.url == "/login/?next=/seller_profile_page/"

    def test_handle_no_permission(self, client):
        # Created a user with invald user type
        user = CustomUserOnlyFactory(
            username="testuser",
            email="testuser@gmail.com",
            password="pass123",
            user_type="CUSTOMER",
        )
        client.force_login(user)

        response = client.get(reverse("Homepage:seller_profile_page"))

        assert response.status_code == 200
        assert "permission_denied.html" in [t.name for t in response.templates]

        user = CustomUser.objects.get(email="testuser@gmail.com", user_type="CUSTOMER")

        pre_defined_user_permissions = user.get_all_permissions()

        assert len(CUSTOMER_CUSTOM_PERMISSIONS) == len(pre_defined_user_permissions)

    def test_form_rendering(self, client):
        # Created a user with invald user type
        user = CustomUserOnlyFactory(
            username="testuser",
            email="testuser@gmail.com",
            password="pass123",
            user_type="SELLER",
        )
        client.force_login(user)

        response = client.get(reverse("Homepage:seller_profile_page"))

        # Check if the response is successful (status code 200)
        assert response.status_code == 200

        # Check that all necessary forms are present in the context
        assert "user_profile_form" in response.context
        assert "seller_profile_form" in response.context
        assert "image_form" in response.context

    def test_image_form(self):

        # Create an image file using Pillow
        image = Image.new("RGB", (100, 100), color="red")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        # Create a SimpleUploadedFile from the image bytes
        uploaded_file = SimpleUploadedFile(
            "test_image.jpg", image_bytes.read(), content_type="image/jpeg"
        )

        # Create the form data
        data = {}
        file_dict = {"image": uploaded_file}
        form = CustomUserImageForm(data, file_dict)

        # Print the form errors for debugging
        print(f"Form errors: {form.errors}")

        # Assert that the form is valid
        assert form.is_valid()

    @patch("Homepage.views.upload")
    @patch("Homepage.views.UserProfileForm")
    @patch("Homepage.views.SellerProfileForm")
    @patch("Homepage.views.CustomUserImageForm")
    def test_seller_successful_profile_update(
        self,
        mock_image_form,
        mock_seller_profile_form,
        mock_user_profile_form,
        mock_upload,
        client: Client,
        user_profile_form_data,
        seller_profile_form_data,
        create_image,
    ):
        client.logout()

        # Configure the mock to return a successful response
        mock_upload.return_value = {"url": "http://example.com/test_image.jpg"}

        user = CustomUser.objects.create(
            email="testuser@example.com",
            username="testuser",
            user_type="SELLER",
        )

        user_profile_model_instance = UserProfile.objects.create(user=user)
        SellerProfile.objects.create(
            seller_profile=user_profile_model_instance, customuser_type_2=user
        )

        client.force_login(user)
        session = client.session
        session["user_id"] = user.id
        session.save()

        # Update session's cookie
        session_cookie_name = settings.SESSION_COOKIE_NAME
        client.cookies[session_cookie_name] = session.session_key

        mock_user_profile_form.return_value.is_valid.return_value = True
        mock_user_profile_form_instance = mock_user_profile_form.return_value
        mock_user_profile_form_instance.save.return_value = Mock()

        mock_seller_profile_form.return_value.is_valid.return_value = True
        mock_seller_profile_form_instance = mock_seller_profile_form.return_value
        mock_seller_profile_form_instance.save.return_value = Mock()

        mock_image_form.return_value.is_valid.return_value = True
        mock_image_form_instance = mock_image_form.return_value
        mock_image_form_instance.save.return_value = Mock()

        userprofileform = UserProfileForm(data=user_profile_form_data)
        print(f"form errors: {userprofileform.errors}")
        assert userprofileform.is_valid()

        assert SellerProfileForm(seller_profile_form_data).is_valid()

        file_dic = create_image

        from Homepage.forms import CustomUserImageForm

        image_form = CustomUserImageForm({"image": file_dic["image"]})
        assert image_form.is_valid()

        data = {
            **user_profile_form_data,
            **seller_profile_form_data,
            "image": file_dic["image"],
        }

        response = client.post(
            reverse("Homepage:seller_profile_page"),
            data=data,
            files=file_dic,
        )

        assert response.status_code == 302
        assert user.image, "http://example.com/test_image.jpg"
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert str(messages[0]) == "Your profile is successfully updated!"
        assert response.url == "/"


@pytest.mark.django_db
class Test_CSRProfilePageViewGet:
    def test_get_authenticated(self, client: Client):

        # Setup for test
        user = CustomUser.objects.create(
            email="testuser@example.com",
            username="testuser",
            password="Testpass123!",
            user_type="CUSTOMER REPRESENTATIVE",
        )

        customer_profile = UserProfile.objects.create(user=user)
        CustomerServiceProfile.objects.create(
            csr_profile=customer_profile, customuser_type_3=user, experience_years=10
        )
        client.force_login(user)
        session = client.session
        session["user_id"] = user.id
        session.save()

        # Update session's cookie
        session_cookie_name = settings.SESSION_COOKIE_NAME
        client.cookies[session_cookie_name] = session.session_key
        response = client.get(reverse("Homepage:csr_profile_page"))

        assert response.status_code == 200
        assert isinstance(response, TemplateResponse)
        assert "csr_profile_page.html" in [t.name for t in response.templates]
        assert "user_id" in response.wsgi_request.session

    def test_get_not_authenticated(self, client, custom_user):
        user, _ = custom_user()
        response = client.get(reverse("Homepage:csr_profile_page"))

        assert response.status_code == 302
        assert response.url == "/login/?next=/csr_profile_page/"

    def test_handle_no_permission(self, client):
        # Created a user with invald user type
        user = CustomUserOnlyFactory(
            username="testuser",
            email="testuser@gmail.com",
            password="pass123",
            user_type="CUSTOMER",
        )
        client.force_login(user)

        response = client.get(reverse("Homepage:csr_profile_page"))

        assert response.status_code == 200
        assert "permission_denied.html" in [t.name for t in response.templates]

        user = CustomUser.objects.get(email="testuser@gmail.com", user_type="CUSTOMER")

        pre_defined_user_permissions = user.get_all_permissions()

        assert len(CUSTOMER_CUSTOM_PERMISSIONS) == len(pre_defined_user_permissions)

    def test_form_rendering(self, client: Client):
        # Setup for test
        user = CustomUser.objects.create(
            email="testuser@example.com",
            username="testuser",
            password="Testpass123!",
            user_type="CUSTOMER REPRESENTATIVE",
        )

        customer_profile = UserProfile.objects.create(user=user)
        CustomerServiceProfile.objects.create(
            csr_profile=customer_profile, customuser_type_3=user, experience_years=10
        )
        client.force_login(user)
        session = client.session
        session["user_id"] = user.id
        session.save()

        # Update session's cookie
        session_cookie_name = settings.SESSION_COOKIE_NAME
        client.cookies[session_cookie_name] = session.session_key

        response = client.get(reverse("Homepage:csr_profile_page"))
        assert response.status_code == 200
        # Check that all necessary forms are present in the context
        assert "user_profile_form" in response.context
        assert "csr_profile_form" in response.context
        assert "image_form" in response.context

    def test_image_form(self):

        # Create an image file using Pillow
        image = Image.new("RGB", (100, 100), color="red")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        # Create a SimpleUploadedFile from the image bytes
        uploaded_file = SimpleUploadedFile(
            "test_image.jpg", image_bytes.read(), content_type="image/jpeg"
        )

        # Create the form data
        data = {}
        file_dict = {"image": uploaded_file}
        form = CustomUserImageForm(data, file_dict)

        # Print the form errors for debugging
        print(f"Form errors: {form.errors}")

        # Assert that the form is valid
        assert form.is_valid()

    @patch("Homepage.views.upload")
    @patch("Homepage.views.UserProfileForm")
    @patch("Homepage.views.CustomerServiceProfileForm")
    @patch("Homepage.views.CustomUserImageForm")
    def test_csr_successful_profile_update(
        self,
        mock_image_form,
        mock_csr_profile_form,
        mock_user_profile_form,
        mock_upload,
        client: Client,
        user_profile_form_data,
        customer_service_profile_form_data,
        create_image,
    ):
        client.logout()

        # Configure the mock to return a successful response
        mock_upload.return_value = {"url": "http://example.com/test_image.jpg"}

        user = CustomUser.objects.create(
            email="testuser@example.com",
            username="testuser",
            user_type="CUSTOMER REPRESENTATIVE",
        )

        user_profile_model_instance = UserProfile.objects.create(user=user)
        CustomerServiceProfile.objects.create(
            csr_profile=user_profile_model_instance,
            customuser_type_3=user,
            experience_years=15,
        )

        client.force_login(user)
        session = client.session
        session["user_id"] = user.id
        session.save()

        # Update session's cookie
        session_cookie_name = settings.SESSION_COOKIE_NAME
        client.cookies[session_cookie_name] = session.session_key

        mock_user_profile_form.return_value.is_valid.return_value = True
        mock_user_profile_form_instance = mock_user_profile_form.return_value
        mock_user_profile_form_instance.save.return_value = Mock()

        mock_csr_profile_form.return_value.is_valid.return_value = True
        mock_csr_profile_form_instance = mock_csr_profile_form.return_value
        mock_csr_profile_form_instance.save.return_value = Mock()

        mock_image_form.return_value.is_valid.return_value = True
        mock_image_form_instance = mock_image_form.return_value
        mock_image_form_instance.save.return_value = Mock()

        userprofileform = UserProfileForm(data=user_profile_form_data)
        print(f"form errors: {userprofileform.errors}")
        assert userprofileform.is_valid()

        assert CustomerServiceProfileForm(customer_service_profile_form_data).is_valid()

        file_dic = create_image

        from Homepage.forms import CustomUserImageForm

        image_form = CustomUserImageForm({"image": file_dic["image"]})
        assert image_form.is_valid()

        data = {
            **user_profile_form_data,
            **customer_service_profile_form_data,
            "image": file_dic["image"],
        }

        response = client.post(
            reverse("Homepage:csr_profile_page"),
            data=data,
            files=file_dic,
        )

        assert response.status_code == 302
        assert user.image, "http://example.com/test_image.jpg"
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert str(messages[0]) == "Your profile is successfully updated!"
        assert response.url == "/"


@pytest.mark.django_db
class Test_ManagerProfilePageViewGet:
    def test_get_authenticated(self, client: Client):
        # Setup for test
        user = CustomUser.objects.create(
            email="testuser@example.com",
            username="testuser",
            user_type="MANAGER",
        )

        user_profile_model_instance = UserProfile.objects.create(user=user)
        ManagerProfile.objects.create(
            manager_profile=user_profile_model_instance,
            customuser_type_4=user,
            experience_years=15,
        )

        client.force_login(user)
        session = client.session
        session["user_id"] = user.id
        session.save()

        # Update session's cookie
        session_cookie_name = settings.SESSION_COOKIE_NAME
        client.cookies[session_cookie_name] = session.session_key
        response = client.get(reverse("Homepage:manager_profile_page"))

        assert response.status_code == 200
        assert isinstance(response, TemplateResponse)
        assert "manager_profile_page.html" in [t.name for t in response.templates]
        assert "user_id" in response.wsgi_request.session

    def test_get_not_authenticated(self, client, custom_user):
        user, _ = custom_user()
        response = client.get(reverse("Homepage:manager_profile_page"))

        assert response.status_code == 302
        assert response.url == "/login/?next=/manager_profile_page/"

    def test_handle_no_permission(self, client):
        # Created a user with invald user type
        user = CustomUserOnlyFactory(
            username="testuser",
            email="testuser@gmail.com",
            password="pass123",
            user_type="SELLER",
        )
        client.force_login(user)

        response = client.get(reverse("Homepage:manager_profile_page"))

        assert response.status_code == 200
        assert "permission_denied.html" in [t.name for t in response.templates]

        user = CustomUser.objects.get(email="testuser@gmail.com", user_type="SELLER")

        pre_defined_user_permissions = user.get_all_permissions()

        assert len(SELLER_CUSTOM_PERMISSIONS) == len(pre_defined_user_permissions)

    def test_form_rendering(self, client: Client):
        # Setup for test
        user = CustomUser.objects.create(
            email="testuser@example.com",
            username="testuser",
            user_type="MANAGER",
        )

        user_profile_model_instance = UserProfile.objects.create(user=user)
        ManagerProfile.objects.create(
            manager_profile=user_profile_model_instance,
            customuser_type_4=user,
            experience_years=15,
        )

        client.force_login(user)
        session = client.session
        session["user_id"] = user.id
        session.save()

        # Update session's cookie
        session_cookie_name = settings.SESSION_COOKIE_NAME
        client.cookies[session_cookie_name] = session.session_key

        response = client.get(reverse("Homepage:manager_profile_page"))
        assert response.status_code == 200
        # Check that all necessary forms are present in the context
        assert "user_profile_form" in response.context
        assert "manager_profile_form" in response.context
        assert "image_form" in response.context

    def test_image_form(self):

        # Create an image file using Pillow
        image = Image.new("RGB", (100, 100), color="red")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        # Create a SimpleUploadedFile from the image bytes
        uploaded_file = SimpleUploadedFile(
            "test_image.jpg", image_bytes.read(), content_type="image/jpeg"
        )

        # Create the form data
        data = {}
        file_dict = {"image": uploaded_file}
        form = CustomUserImageForm(data, file_dict)

        # Print the form errors for debugging
        print(f"Form errors: {form.errors}")

        # Assert that the form is valid
        assert form.is_valid()

    @patch("Homepage.views.upload")
    @patch("Homepage.views.UserProfileForm")
    @patch("Homepage.views.ManagerProfileForm")
    @patch("Homepage.views.CustomUserImageForm")
    def test_manager_successful_profile_update(
        self,
        mock_image_form,
        mock_manager_profile_form,
        mock_user_profile_form,
        mock_upload,
        client: Client,
        user_profile_form_data,
        manager_profile_form_data,
        create_image,
    ):
        client.logout()

        # Configure the mock to return a successful response
        mock_upload.return_value = {"url": "http://example.com/test_image.jpg"}

        user = CustomUser.objects.create(
            email="testuser@example.com",
            username="testuser",
            user_type="MANAGER",
        )

        user_profile_model_instance = UserProfile.objects.create(user=user)
        ManagerProfile.objects.create(
            manager_profile=user_profile_model_instance,
            customuser_type_4=user,
            experience_years=15,
        )

        client.force_login(user)
        session = client.session
        session["user_id"] = user.id
        session.save()

        # Update session's cookie
        session_cookie_name = settings.SESSION_COOKIE_NAME
        client.cookies[session_cookie_name] = session.session_key

        mock_user_profile_form.return_value.is_valid.return_value = True
        mock_user_profile_form_instance = mock_user_profile_form.return_value
        mock_user_profile_form_instance.save.return_value = Mock()

        mock_manager_profile_form.return_value.is_valid.return_value = True
        mock_manager_profile_form_instance = mock_manager_profile_form.return_value
        mock_manager_profile_form_instance.save.return_value = Mock()

        mock_image_form.return_value.is_valid.return_value = True
        mock_image_form_instance = mock_image_form.return_value
        mock_image_form_instance.save.return_value = Mock()

        userprofileform = UserProfileForm(data=user_profile_form_data)
        print(f"form errors: {userprofileform.errors}")
        assert userprofileform.is_valid()

        assert ManagerProfileForm(manager_profile_form_data).is_valid()

        file_dic = create_image

        from Homepage.forms import CustomUserImageForm

        image_form = CustomUserImageForm({"image": file_dic["image"]})
        assert image_form.is_valid()

        data = {
            **user_profile_form_data,
            **manager_profile_form_data,
            "image": file_dic["image"],
        }

        response = client.post(
            reverse("Homepage:manager_profile_page"),
            data=data,
            files=file_dic,
        )

        assert response.status_code == 302
        assert user.image, "http://example.com/test_image.jpg"
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert str(messages[0]) == "Your profile is successfully updated!"
        assert response.url == "/"


@pytest.mark.django_db
class Test_AdministratorProfilePageViewGet:
    def test_get_authenticated(self, group_user_logged_in):
        user = CustomUserFactory(
            username="testuser",
            user_type="ADMINISTRATOR",
            email="testuser@gmail.com",
        )
        client = group_user_logged_in(user)
        response = client.get(reverse("Homepage:admin_profile_page"))

        assert response.status_code == 200
        assert "admin_profile_page.html" in [t.name for t in response.templates]
        assert "user_id" in response.wsgi_request.session

    def test_get_not_authenticated(self, client, custom_user):
        user, _ = custom_user()
        response = client.get(reverse("Homepage:manager_profile_page"))

        assert response.status_code == 302
        assert response.url == "/login/?next=/manager_profile_page/"

    def test_handle_no_permission(self, client):
        # Created a user with invald user type
        user = CustomUserOnlyFactory(
            username="testuser",
            email="testuser@gmail.com",
            password="pass123",
            user_type="SELLER",
        )
        client.force_login(user)

        response = client.get(reverse("Homepage:admin_profile_page"))

        assert response.status_code == 200
        assert "permission_denied.html" in [t.name for t in response.templates]

        user = CustomUser.objects.get(email="testuser@gmail.com", user_type="SELLER")

        pre_defined_user_permissions = user.get_all_permissions()

        assert len(SELLER_CUSTOM_PERMISSIONS) == len(pre_defined_user_permissions)

    def test_form_rendering(self, client):
        # Created a user with invald user type
        user = CustomUserOnlyFactory(
            username="testuser",
            email="testuser@gmail.com",
            password="pass123",
            user_type="ADMINISTRATOR",
        )
        client.force_login(user)

        response = client.get(reverse("Homepage:admin_profile_page"))

        # Check if the response is successful (status code 200)
        assert response.status_code == 200

        # Check that all necessary forms are present in the context
        assert "user_profile_form" in response.context
        assert "admin_profile_form" in response.context
        assert "image_form" in response.context

    def test_image_form(self):

        # Create an image file using Pillow
        image = Image.new("RGB", (100, 100), color="red")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        # Create a SimpleUploadedFile from the image bytes
        uploaded_file = SimpleUploadedFile(
            "test_image.jpg", image_bytes.read(), content_type="image/jpeg"
        )

        # Create the form data
        data = {}
        file_dict = {"image": uploaded_file}
        form = CustomUserImageForm(data, file_dict)

        # Print the form errors for debugging
        print(f"Form errors: {form.errors}")

        # Assert that the form is valid
        assert form.is_valid()

    @patch("Homepage.views.upload")
    @patch("Homepage.views.UserProfileForm")
    @patch("Homepage.views.AdministratorProfileForm")
    @patch("Homepage.views.CustomUserImageForm")
    def test_admin_successful_profile_update(
        self,
        mock_image_form,
        mock_admin_profile_form,
        mock_user_profile_form,
        mock_upload,
        client: Client,
        user_profile_form_data,
        admin_profile_form_data,
        create_image,
    ):
        client.logout()

        # Configure the mock to return a successful response
        mock_upload.return_value = {"url": "http://example.com/test_image.jpg"}

        user = CustomUser.objects.create(
            email="testuser@example.com",
            username="testuser",
            user_type="ADMINISTRATOR",
        )

        user_profile_model_instance = UserProfile.objects.create(user=user)
        AdministratorProfile.objects.create(
            admin_profile=user_profile_model_instance,
            user=user,
            experience_years=15,
        )

        client.force_login(user)
        session = client.session
        session["user_id"] = user.id
        session.save()

        # Update session's cookie
        session_cookie_name = settings.SESSION_COOKIE_NAME
        client.cookies[session_cookie_name] = session.session_key

        mock_user_profile_form.return_value.is_valid.return_value = True
        mock_user_profile_form_instance = mock_user_profile_form.return_value
        mock_user_profile_form_instance.save.return_value = Mock()

        mock_admin_profile_form.return_value.is_valid.return_value = True
        mock_admin_profile_form_instance = mock_admin_profile_form.return_value
        mock_admin_profile_form_instance.save.return_value = Mock()

        mock_image_form.return_value.is_valid.return_value = True
        mock_image_form_instance = mock_image_form.return_value
        mock_image_form_instance.save.return_value = Mock()

        userprofileform = UserProfileForm(data=user_profile_form_data)
        print(f"form errors: {userprofileform.errors}")
        assert userprofileform.is_valid()

        assert AdministratorProfileForm(admin_profile_form_data).is_valid()

        file_dic = create_image

        from Homepage.forms import CustomUserImageForm

        image_form = CustomUserImageForm({"image": file_dic["image"]})
        assert image_form.is_valid()

        data = {
            **user_profile_form_data,
            **admin_profile_form_data,
            "image": file_dic["image"],
        }

        response = client.post(
            reverse("Homepage:admin_profile_page"),
            data=data,
            files=file_dic,
        )

        assert response.status_code == 302
        assert user.image, "http://example.com/test_image.jpg"
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert str(messages[0]) == "Your profile is successfully updated!"
        assert response.url == "/"


@pytest.mark.django_db()
class Test_ValidateUserView:

    def test_get_request_renders_form(self, client: Client):
        # Test GET request to render the email form
        response = client.get(reverse("Homepage:send_sms"))
        assert response.status_code == 200
        assert "password_reset_email.html" in [t.name for t in response.templates]
        assert isinstance(response.context["form"], E_MailForm_For_Password_Reset)

    @patch("Homepage.views.helper_function")
    def test_post_request_valid_email_sends_otp(self, helper_function, custom_user):
        # Make a client
        client = Client(
            HTTP_USER_AGENT="Mozilla/5.0",
            HTTP_REFERER=reverse("Homepage:login"),
        )

        # Clear Cache
        cache.clear()

        user, user_profile = custom_user()
        email = user.email

        user_profile = UserProfile.objects.get(user__id=user.id)
        user_profile.phone_number = "+923074649892"
        user_profile.save()

        # Test POST request with a valid email and phone number
        helper_function.return_value = True  # Mock Twilio API call as success
        response = client.post(reverse("Homepage:send_sms"), data={"email": email})

        # Check OTP message success in response and redirection
        assert response.status_code == 302

        temporary_cookie = json.loads(response.cookies.get("temporary_cookie").value)

        assert temporary_cookie["referer_url"] == reverse("Homepage:login")
        assert response.url == reverse("Homepage:validate_otp_view")

        # Tear Down Cookies and Cache
        cache.clear()
        response.delete_cookie("temporary_cookie")
        assert response.cookies.get("temporary_cookie")["max-age"] == 0

    @patch("Homepage.views.helper_function")
    def test_post_request_invalid_email_redirects_signup(
        self, helper_function, client: Client
    ):
        # Test with an invalid email (no associated user)
        helper_function.return_value = True
        response = client.post(
            reverse("Homepage:send_sms"), data={"email": "nonexistent@example.com"}
        )

        assert response.status_code == 302
        assert response.url == reverse("Homepage:signup")

    def test_post_request_no_phone_number_redirects_password_reset(
        self, client: Client, custom_user
    ):
        # Create a User with UserProfile object containing empty string as phone_number
        user, user_profile = custom_user()

        response = client.post(reverse("Homepage:send_sms"), data={"email": user.email})

        messages = list(get_messages(response.wsgi_request))
        assert response.status_code == 302
        assert response.url == reverse("Homepage:password_reset")
        assert any("Your profile is not updated" in str(msg) for msg in messages)

    @patch("Homepage.views.helper_function")
    def test_post_request_otp_sending_failure(
        self, helper_function, client: Client, custom_user
    ):
        user, user_profile = custom_user()
        email = user.email

        user_profile = UserProfile.objects.get(user__id=user.id)
        user_profile.phone_number = "+923074649892"
        user_profile.save()

        # Simulate OTP sending failure
        helper_function.return_value = False

        response = client.post(reverse("Homepage:send_sms"), data={"email": email})

        messages = list(get_messages(response.wsgi_request))
        assert response.status_code == 302
        assert response.url == reverse("Homepage:login")
        assert any("Failed to send SMS" in str(msg) for msg in messages)


@pytest.mark.django_db
class Test_ValidateOtpView:

    def test_successful_otp_validation(
        self,
        client: Client,
        custom_user,
    ):

        # 1. create user
        user, user_profile = custom_user()
        email = user.email
        # 2. update user profile
        user_profile = UserProfile.objects.get(user__id=user.id)
        user_profile.phone_number = "+923074649892"
        user_profile.save()

        # clearing cache and cookie previously created
        cache.clear()
        if client.cookies.get("temporary_cookie"):
            client.cookies.get("temporary_cookie")["max-age"] == 0

        # Setup For POST request to "validate_otp_view"
        client = Client()
        client.cookies["temporary_cookie"] = json.dumps(
            {
                "email": email,
                "id": user.id,
                "generated_otp": str(123456),
                "referer_url": reverse("Homepage:login"),
            }
        )
        # Act
        response = client.post(
            reverse("Homepage:validate_otp_view"), data={"otp": 123456}
        )
        # Assertions
        assert response.status_code == 302
        assert response.url == "/"
        messages = list(get_messages(response.wsgi_request))
        assert any("Successfully Logged In" in str(msg) for msg in messages)

        # Tear Down Cookies and Cache
        cache.clear()
        response.delete_cookie("temporary_cookie")
        assert response.cookies.get("temporary_cookie")["max-age"] == 0

    def test_invalid_otp(self, client: Client, custom_user):

        # Create user
        user, user_profile = custom_user()
        email = user.email

        invalid_otp = "654321"

        client.cookies["temporary_cookie"] = json.dumps(
            {
                "email": email,
                "id": user.id,
                "generated_otp": "123456",
                "referer_url": reverse("Homepage:login"),
            }
        )

        response = client.post(
            reverse("Homepage:validate_otp_view"), {"otp": invalid_otp}
        )

        assert response.status_code == 302
        assert response.url == reverse("Homepage:validate_otp_view")
        messages = list(get_messages(response.wsgi_request))
        assert any("Invalid OTP. Please try again." in str(msg) for msg in messages)

    def test_get_request_displays_otp_form(self, client: Client):
        response = client.get(reverse("Homepage:validate_otp_view"))

        assert response.status_code == 200
        assert "otp.html" in [template.name for template in response.templates]
        assert isinstance(response.context["form"], OTPForm)


@pytest.mark.django_db
class Test_CustomPasswordResetConfirmViaOTPView:

    def test_password_reset_confirm_valid_form(self, client: Client, custom_user):
        """Test valid form submission for password reset."""

        # 1. create user
        user, user_profile = custom_user()
        email = user.email

        # Setup For POST request to "validate_otp_view"
        client.cookies["temporary_cookie"] = json.dumps(
            {
                "email": email,
                "id": user.id,
                "generated_otp": str(123456),
                "referer_url": reverse("Homepage:login"),
            }
        )

        url = reverse("Homepage:password_reset_confirm_via_otp")
        data = {
            "new_password1": "New_password123!",
            "new_password2": "New_password123!",
        }

        response = client.post(url, data)

        # Verify redirection to password reset complete page
        assert response.status_code == 302
        assert response.url == reverse("Homepage:password_reset_complete")
        # Verify cookie is deleted
        assert response.cookies.get("temporary_cookie")["max-age"] == 0

    def test_password_reset_confirm_password_mismatch(
        self, client: Client, custom_user
    ):
        """Test password mismatch scenario."""

        # 1. create user
        user, user_profile = custom_user()
        email = user.email
        # 2. update user profile
        user_profile = UserProfile.objects.get(user__id=user.id)
        user_profile.phone_number = "+923074649892"
        user_profile.save()

        # Setup For POST request to "validate_otp_view"
        client.cookies["temporary_cookie"] = json.dumps(
            {
                "email": email,
                "id": user.id,
                "generated_otp": str(123456),
                "referer_url": reverse("Homepage:login"),
            }
        )

        url = reverse("Homepage:password_reset_confirm_via_otp")
        data = {
            "new_password1": "New_password123!",
            "new_password2": "Different_password!",
        }

        response = client.post(url, data)

        # Verify response renders the same template with an error message
        assert response.status_code == 200
        message = list(get_messages(response.wsgi_request))[0].message
        assert "Passwords does not match" == message

    def test_password_reset_confirm_invalid_form(self, client: Client, custom_user):
        """Test invalid form submission (e.g., missing fields)."""

        # 1. create user
        user, user_profile = custom_user()
        email = user.email
        # 2. update user profile
        user_profile = UserProfile.objects.get(user__id=user.id)
        user_profile.phone_number = "+923074649892"
        user_profile.save()

        # Setup For POST request to "validate_otp_view"
        client.cookies["temporary_cookie"] = json.dumps(
            {
                "email": email,
                "id": user.id,
                "generated_otp": str(123456),
                "referer_url": reverse("Homepage:login"),
            }
        )

        url = reverse("Homepage:password_reset_confirm_via_otp")
        data = {
            "new_password1": "new_password",
            "new_password2": "new_password",
        }

        response = client.post(url, data)

        # Verify response renders the same template with an error message
        assert response.status_code == 200
        message = list(get_messages(response.wsgi_request))[0].message
        assert "Form Not Valid" == message

    def test_password_reset_confirm_no_temporary_cookie(self, client: Client):
        """Test view redirect when temporary cookie is missing."""

        url = reverse("Homepage:password_reset_confirm_via_otp")
        data = {"new_password1": "new_password123", "new_password2": "new_password123"}

        response = client.post(url, data)

        # Verify redirection to send_sms page
        assert response.status_code == 302
        assert response.url == reverse("Homepage:send_sms")
