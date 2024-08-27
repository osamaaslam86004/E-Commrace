import pytest
from unittest.mock import patch, Mock
from cv_api.create_read_update_delete_user import TokenUtils
from Homepage.models import UserProfile
from tests.cv_api.cv_api_factory import CustomUserOnlyFactory
import logging


# Disable Faker DEBUG logging
faker_logger = logging.getLogger("faker")
faker_logger.setLevel(logging.WARNING)


@pytest.fixture
def create_user():
    def _create_user():
        user = CustomUserOnlyFactory()

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
        return user

    return _create_user


@pytest.mark.django_db
def test_register_user(create_user):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "access": "access_token",
            "refresh": "refresh_token",
        }
        mock_post.return_value = mock_response

        response = TokenUtils.register_user(create_user())

        assert response == {"access": "access_token", "refresh": "refresh_token"}
        mock_post.assert_called_once()


@pytest.mark.django_db
def test_get_user(create_user):
    user = create_user()

    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": user.id}
        mock_post.return_value = mock_response

        response = TokenUtils.get_user(user)

        assert response == {"id": user.id}
        mock_post.assert_called_once()


@pytest.mark.django_db
def test_get_tokens_for_user(create_user):
    user = create_user()

    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access": "access_token",
            "refresh": "refresh_token",
        }
        mock_post.return_value = mock_response

        response = TokenUtils.get_tokens_for_user(user.id)

        assert response == {"access": "access_token", "refresh": "refresh_token"}
        mock_post.assert_called_once()


def test_get_new_access_token_for_user():
    refresh_token = "dummy_refresh_token"
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access": "new_access_token"}
        mock_post.return_value = mock_response

        response = TokenUtils.get_new_access_token_for_user(refresh_token)

        assert response == "new_access_token"
        mock_post.assert_called_once()


def test_verify_access_token_for_user():
    access_token = "dummy_access_token"
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        response = TokenUtils.verify_access_token_for_user(access_token)

        assert response is True
        mock_post.assert_called_once()

        mock_response.status_code = 400
        mock_post.return_value = mock_response
        response = TokenUtils.verify_access_token_for_user(access_token)
        assert response is False
