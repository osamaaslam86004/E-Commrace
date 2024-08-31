import pytest
import logging
import requests
import json
from django.http.response import JsonResponse
from django.urls import reverse
from django.contrib.messages import get_messages
from django.test import Client
from unittest.mock import patch, Mock
from cv_api.models import TokensForUser, PersonalInfo
from Homepage.models import UserProfile
from tests.cv_api.cv_api_factory import (
    CustomUserOnlyFactory,
    PersonalInfoFactory,
    TokensForUserFactory,
    OverviewFactory,
    JobAccomplishmentFactory,
    JobFactory,
    EducationFactory,
    SkillAndSkillLevelFactory,
    ProgrammingAreaFactory,
    ProjectsFactory,
    PublicationFactory,
)
from cv_api.forms import (
    PersonalInfoForm,
    OverviewForm,
    EducationfoForm,
    JobfoForm,
    JobAccomplishmentfoForm,
    ProjectsForm,
    ProgrammingAreaForm,
    SkillAndSkillLevelForm,
    PublicationForm,
)
from django_mock_queries.query import MockSet
from django_mock_queries.mocks import mocked_relations


# Disable Faker DEBUG logging
faker_logger = logging.getLogger("faker")
faker_logger.setLevel(logging.WARNING)


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def custom_user():
    def _custom_user():
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
        return user, user_profile

    return _custom_user


@pytest.fixture
def login_form_data():
    def _login_form_data(user):
        return {
            "email": user.email,
            "password": "testpass123",
        }

    return _login_form_data


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
def token_instance(client_logged_in):
    client, user = client_logged_in

    token_instance = TokensForUser.objects.create(
        user=user,
        access_token="initial_access_token",
        refresh_token="initial_refresh_token",
    )
    return token_instance


@pytest.fixture
def mock_personalinfo_create():
    def _mock_personalinfo_create_(user):
        mock_personal_info = PersonalInfoFactory(user_id_for_personal_info=user)
        mock_personal_info_set = MockSet(mock_personal_info)
        return mock_personal_info, mock_personal_info_set

    return _mock_personalinfo_create_


@pytest.fixture
def mock_select_related_query():
    def _mock_select_related_(user):
        mock_personal_info_batch = PersonalInfoFactory.create_batch(
            5, user_id_for_personal_info=user
        )
        return mock_personal_info_batch

    return _mock_select_related_


@pytest.fixture
def mock_TokenrForUser_create():
    def _mock_TokenForUser_create_(user):
        mock_token_instance = TokensForUserFactory(user=user)
        mock_token_instance.access_token = "access_token"
        mock_token_instance.refresh_token = "refresh_token"

        mock_token_instance_set = MockSet(mock_token_instance)
        return mock_token_instance, mock_token_instance_set

    return _mock_TokenForUser_create_


@pytest.fixture
def mock_personalinfo_delete(mocker):
    mocker.patch.object(PersonalInfo, "delete")
    return PersonalInfo.delete


@pytest.fixture
def mock_relations_personal_info():
    with mocked_relations(PersonalInfo):
        yield


@pytest.fixture
def personal_info_data():
    def _personal_info_data(user):

        personal_info_instance = PersonalInfoFactory.create(
            user_id_for_personal_info=user
        )
        overview_instance = OverviewFactory.create()
        education_instances = [EducationFactory.create() for _ in range(2)]
        job_instance = JobFactory.create()
        job_accomplishment_instance = JobAccomplishmentFactory.create()
        skill_and_skill_level_instances = SkillAndSkillLevelFactory.create()
        programming_area_instances = ProgrammingAreaFactory.create()
        projects_instances = [ProjectsFactory.create() for _ in range(2)]
        publication_instances = [PublicationFactory.create() for _ in range(2)]

        json_data = {
            "first_name": personal_info_instance.first_name,
            "middle_name": personal_info_instance.middle_name,
            "last_name": personal_info_instance.last_name,
            "suffix": personal_info_instance.suffix,
            "locality": personal_info_instance.locality,
            "region": personal_info_instance.region,
            "title": personal_info_instance.title,
            "email": personal_info_instance.email,
            "linkedin": personal_info_instance.linkedin,
            "facebook": personal_info_instance.facebook,
            "github": personal_info_instance.github,
            "site": personal_info_instance.site,
            "twittername": personal_info_instance.twittername,
            "overview": {
                "text": overview_instance.text,
            },
            "education": [
                {
                    "name": instance.name,
                    "location": instance.location,
                    "schoolurl": instance.schoolurl,
                    # factoryboy already created this field in ISO Format
                    "education_start_date": instance.education_start_date,
                    "education_end_date": instance.education_end_date,
                    "degree": instance.degree,
                    "description": instance.description,
                }
                for instance in education_instances
            ],
            "job": {
                "company": job_instance.company,
                "companyurl": job_instance.companyurl,
                "location": job_instance.location,
                "title": job_instance.title,
                "description": job_instance.description,
                "job_start_date": job_instance.job_start_date,
                "job_end_date": job_instance.job_end_date,
                "is_current": job_instance.is_current,
                "is_public": job_instance.is_public,
                "image": job_instance.image,
                "accomplishment": {
                    "job_accomplishment": job_accomplishment_instance.job_accomplishment,
                },
            },
            "skill": [
                {
                    "text": skill_and_skill_level_instances.text,
                    "skill_level": skill_and_skill_level_instances.skill_level,
                }
            ],
            "programming_area": [
                {
                    "programming_area_name": programming_area_instances.programming_area_name,
                    "programming_language_name": programming_area_instances.programming_language_name,
                }
            ],
            "projects": [
                {
                    "project_name": instance.project_name,
                    "short_description": instance.short_description,
                    "long_description": instance.long_description,
                    "link": instance.link,
                }
                for instance in projects_instances
            ],
            "publications": [
                {
                    "title": instance.title,
                    "authors": instance.authors,
                    "journal": instance.journal,
                    "year": instance.year,
                    "link": instance.link,
                }
                for instance in publication_instances
            ],
        }

        return json_data, personal_info_instance, user

    return _personal_info_data


@pytest.fixture
def keys_adjusted_personal_info_data():
    def _keys_adjusted_personal_info_data_(data):
        keys_in_data = [
            "overview",
            "skill",
            "projects",
            "publications",
            "job",
            "programming_area",
            "education",
        ]
        personal_info = data.copy()

        cookie_data = {}

        for key in keys_in_data:
            if key in personal_info:
                if key == "overview":
                    cookie_data["overview_text"] = personal_info.pop("overview")
                elif key == "education":
                    cookie_data["education_data"] = personal_info.pop("education")
                elif key == "job":
                    cookie_data["job_data"] = personal_info.pop("job")
                    if "accomplishment" in cookie_data["job_data"]:
                        cookie_data["accomplishment_data"] = cookie_data[
                            "job_data"
                        ].pop("accomplishment")
                elif key == "programming_area":
                    cookie_data["programming_area_data"] = personal_info.pop(
                        "programming_area"
                    )
                elif key == "skill":
                    cookie_data["skill_data"] = personal_info.pop("skill")
                elif key == "projects":
                    cookie_data["projects_data"] = personal_info.pop("projects")
                elif key == "publications":
                    cookie_data["publications"] = personal_info.pop("publications")

        # Add remaining personal_info to cookie_data
        cookie_data["personal_info"] = personal_info

        return cookie_data

    return _keys_adjusted_personal_info_data_


@pytest.fixture
def data_to_post():
    def _data_to_post_(data):
        data_to_post = {
            "personal_info": data["personal_info"],
            "overview_text": data["overview_text"],
            "job_data": data["job_data"],
            "accomplishment_data": data["accomplishment_data"],
        }

        # Add education data as a list of dictionaries
        data_to_post["education"] = []
        for education in data["education_data"]:
            data_to_post["education"].append(
                {
                    "name": education["name"],
                    "location": education["location"],
                    "schoolurl": education["schoolurl"],
                    "education_start_date": education["education_start_date"],
                    "education_end_date": education["education_end_date"],
                    "degree": education["degree"],
                    "description": education["description"],
                }
            )

        # Add skill data as a list of dictionaries
        data_to_post["skill_data"] = []
        for skill in data["skill_data"]:
            data_to_post["skill_data"].append(
                {
                    "text": skill["text"],
                    "skill_level": skill["skill_level"],
                }
            )

        # Add programming area data as a list of dictionaries
        data_to_post["programming_area_data"] = []
        for programming_area in data["programming_area_data"]:
            data_to_post["programming_area_data"].append(
                {
                    "programming_area_name": programming_area["programming_area_name"],
                    "programming_language_name": programming_area[
                        "programming_language_name"
                    ],
                }
            )

        # Add projects data as a list of dictionaries
        data_to_post["projects_data"] = []
        for project in data["projects_data"]:
            data_to_post["projects_data"].append(
                {
                    "project_name": project["project_name"],
                    "short_description": project["short_description"],
                    "long_description": project["long_description"],
                    "link": project["link"],
                }
            )

        # Add publications data as a list of dictionaries
        data_to_post["publications"] = []
        for publication in data["publications"]:
            data_to_post["publications"].append(
                {
                    "title": publication["title"],
                    "authors": publication["authors"],
                    "journal": publication["journal"],
                    "year": publication["year"],
                    "link": publication["link"],
                }
            )
        return data_to_post

    return _data_to_post_


# Additional assertions to check context keys
expected_keys = [
    "form",
    "overview_form",
    "education_form",
    "job_form",
    "accomplishment_form",
    "skill_form",
    "programming_area_form",
    "projects_form",
    "publication_form",
]


@pytest.mark.django_db
class Test_CVAPIPostrequest:
    @patch("cv_api.views.TokenUtils.get_user")
    @patch("cv_api.views.TokenUtils.register_user")
    @patch("cv_api.views.TokenUtils.get_tokens_for_user")
    @patch("cv_api.views.TokenUtils.verify_access_token_for_user")
    @patch("cv_api.views.TokenUtils.get_new_access_token_for_user")
    def test_get_method(
        self,
        mock_get_new_access_token_for_user,
        mock_verify_access_token_for_user,
        mock_get_tokens_for_user,
        mock_register_user,
        mock_get_user,
        client_logged_in,
        token_instance,
    ):
        client, user = client_logged_in
        # Mock the external utility functions
        mock_get_user.return_value = {"id": user.id}
        mock_register_user.return_value = {"id": user.id}
        mock_get_tokens_for_user.return_value = {
            "access": "new_access_token",
            "refresh": "new_refresh_token",
        }
        mock_verify_access_token_for_user.return_value = True
        mock_get_new_access_token_for_user.return_value = "new_access_token"

        # Call the get method
        response = client.get(reverse("cv_api:cv_view"))

        # Assertions
        assert response.status_code == 200
        token_instance.refresh_from_db()
        assert token_instance.access_token == "new_access_token"
        assert token_instance.refresh_token == "new_refresh_token"

        assert "cv.html" in [t.name for t in response.templates]


class Test_CVApiSubmitForm:
    @pytest.mark.django_db
    def test_get_api_user_id_with_personal_info(self, client_logged_in):
        client, user = client_logged_in

        mock_personal_info = PersonalInfo(
            user_id_for_personal_info=user, api_user_id_for_cv="12345"
        )

        mock_personal_info_set = MockSet(mock_personal_info)

        with patch(
            "cv_api.models.PersonalInfo.objects.filter",
            return_value=mock_personal_info_set,
        ) as mock_filter:
            response = client.get(reverse("cv_api:submit_form"))

            assert response.status_code == 302  # Redirect status code
            assert response.url.endswith("resume/?user_id=12345")

            mock_filter.assert_called_once_with(user_id_for_personal_info__id=user.id)

    @pytest.mark.django_db
    def test_get_api_user_id_without_personal_info(self, client_logged_in):
        client, user = client_logged_in

        mock_tokens_for_user = TokensForUser(user=user)
        mock_token_set = MockSet(mock_tokens_for_user)

        mock_user_data = {"id": "67890"}

        mock_personal_info = PersonalInfo(
            user_id_for_personal_info=user,
            api_user_id_for_cv=mock_user_data["id"],
            api_id_of_cv="9999999",
        )

        mock_personal_info_set = MockSet(mock_personal_info)

        with patch(
            "cv_api.models.TokensForUser.objects.filter", return_value=mock_token_set
        ):
            with patch(
                "cv_api.models.PersonalInfo.objects.create",
                return_value=mock_personal_info_set,
            ) as mock_instance:
                with patch(
                    "cv_api.create_read_update_delete_user.TokenUtils.get_user",
                    return_value=mock_user_data,
                ) as mock_get_user:

                    response = client.get(reverse("cv_api:submit_form"))

                    assert response.status_code == 302  # Redirect status code
                    assert response.url.endswith("resume/?user_id=67890")

                    mock_instance.assert_called_once_with(
                        user_id_for_personal_info=user,
                        api_user_id_for_cv=mock_user_data["id"],
                        api_id_of_cv="9999999",
                    )
                    mock_get_user.assert_called_once_with(user)


class Test_ListOfCVForUser:
    @pytest.mark.django_db
    def test_user_has_valid_token_and_personal_info(self, client_logged_in):
        client, user = client_logged_in

        mock_tokens_for_user = TokensForUser(user=user, access_token="valid_token")
        mock_token_set = MockSet(mock_tokens_for_user)

        mock_personal_info = PersonalInfo(
            user_id_for_personal_info=user,
            api_user_id_for_cv="12345",
            api_id_of_cv="9999999",
        )
        mock_personal_info_set = MockSet(mock_personal_info)

        cv_data_response = {"cv": "data"}

        with patch(
            "cv_api.models.TokensForUser.objects.filter", return_value=mock_token_set
        ):
            with patch(
                "cv_api.models.PersonalInfo.objects.filter",
                return_value=mock_personal_info_set,
            ):
                with patch("requests.get") as mock_get:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_get.json.return_value = cv_data_response

                    response = client.get(reverse("cv_api:list_of_cv_for_user"))

                    assert response.status_code == 200
                    assert "cv_data" in response.context

    @pytest.mark.django_db
    def test_user_has_valid_token_but_no_personal_info(self, client_logged_in):
        client, user = client_logged_in

        mock_personal_info = PersonalInfo(
            user_id_for_personal_info=user,
            api_user_id_for_cv="12345",
            api_id_of_cv="9999999",
        )
        mock_personalinfo_instance_set = MockSet(mock_personal_info)

        mock_tokens_for_user = TokensForUser(user=user, access_token="valid_token")
        mock_token_set = MockSet(mock_tokens_for_user)

        with patch(
            "cv_api.models.TokensForUser.objects.filter", return_value=mock_token_set
        ):
            with patch(
                "cv_api.models.PersonalInfo.objects.create",
                return_value=mock_personalinfo_instance_set,
            ):
                response = client.get(reverse("cv_api:list_of_cv_for_user"))

                assert response.status_code == 200
                assert "cv_data" in response.context
                assert response.context["cv_data"] is None

    @pytest.mark.django_db
    def test_user_does_not_have_valid_token(self, client_logged_in):
        client, user = client_logged_in

        with patch(
            "cv_api.models.TokensForUser.objects.filter", return_value=MockSet()
        ):
            response = client.get(reverse("cv_api:list_of_cv_for_user"))

            assert response.status_code == 200
            assert "cv_data" in response.context
            assert response.context["cv_data"] is None

    @pytest.mark.django_db
    def test_error_fetching_cv_data(self, client_logged_in):
        client, user = client_logged_in

        mock_tokens_for_user = TokensForUser(user=user, access_token="valid_token")
        mock_token_set = MockSet(mock_tokens_for_user)

        mock_personal_info = PersonalInfo(
            user_id_for_personal_info=user,
            api_user_id_for_cv="12345",
            api_id_of_cv="9999999",
        )
        mock_personal_info_set = MockSet(mock_personal_info)

        with patch(
            "cv_api.models.TokensForUser.objects.filter", return_value=mock_token_set
        ):
            with patch(
                "cv_api.models.PersonalInfo.objects.filter",
                return_value=mock_personal_info_set,
            ):
                with patch("requests.get") as mock_get:
                    mock_response = Mock()
                    mock_response.status_code = 500
                    mock_get.return_value = mock_response

                    response = client.get(reverse("cv_api:list_of_cv_for_user"))

                    assert response.status_code == 200
                    assert "cv_data" in response.context
                    assert response.context["cv_data"] is None


@pytest.mark.django_db
class Test_DeleteCVForUser:
    def test_delete_cv_for_user_with_valid_token_and_id(
        self, client_logged_in, mock_personalinfo_create, mock_TokenrForUser_create
    ):
        client, user = client_logged_in

        # Mock TokenForUser instance
        token_instance, mock_token_instance_set = mock_TokenrForUser_create(user)

        # Mock PersonalInfo create
        personalinfo_instance, mock_personal_info_set = mock_personalinfo_create(user)

        # Mock the seletc_related
        select_related_query_set = MockSet(personalinfo_instance)

        # Mock response json data
        mock_response_json_data = {
            "status": "DELETED",
            "id": personalinfo_instance.api_id_of_cv,
            "user_id": personalinfo_instance.api_user_id_for_cv,
        }
        with patch(
            "cv_api.models.TokensForUser.objects.filter",
            return_value=mock_token_instance_set,
        ) as mock_tokens_for_user_filter:

            with patch("requests.delete") as mock_requests_delete:
                mock_response = Mock()
                mock_response.status_code = 204
                mock_response.json.return_value = mock_response_json_data
                mock_requests_delete.return_value = mock_response

                with patch(
                    "cv_api.models.PersonalInfo.objects.select_related",
                    return_value=select_related_query_set,
                ) as mock_personal_info_select_related:

                    with patch(
                        "cv_api.models.PersonalInfo.objects.filter"
                    ) as mock_personalinfo_queryset:
                        mock_personalinfo_queryset.first.return_value = (
                            mock_personal_info_set
                        )

                        response = client.get(
                            reverse(
                                "cv_api:get_cv_to_delete",
                                kwargs={"personal_info_id": personalinfo_instance.id},
                            ),
                        )

                        assert response.status_code == 301
                        # Check the response redirect URL
                        assert response.url == "/"
                        # Access messages from the response
                        messages = list(get_messages(response.wsgi_request))
                        assert any(
                            "Cv DELETED successfully!" in str(message)
                            for message in messages
                        )
                # Additional assertions to ensure mocks are called as expected
        mock_tokens_for_user_filter.assert_called_once_with(user__id=user.id)
        mock_requests_delete.assert_called_once()
        mock_personal_info_select_related.assert_called_once()

    @pytest.mark.django_db
    def test_delete_cv_for_user_with_no_token(
        self, client_logged_in, mock_personalinfo_create
    ):
        client, user = client_logged_in

        # Mock PersonalInfo create
        instance, mock_personal_info_set = mock_personalinfo_create(user)
        with patch(
            "cv_api.models.PersonalInfo.objects.filter",
            return_value=mock_personal_info_set,
        ):
            with patch(
                "cv_api.models.TokensForUser.objects.filter", return_value=MockSet()
            ):
                response = client.get(
                    reverse(
                        "cv_api:get_cv_to_delete",
                        kwargs={"personal_info_id": instance.id},
                    ),
                )

                assert response.status_code == 301
                # Check the response redirect URL
                assert response.url == "/"
                # Access messages from the response
                messages = list(get_messages(response.wsgi_request))
                assert any(
                    "Token not found for user." in str(message) for message in messages
                )

    @pytest.mark.django_db
    def test_delete_cv_for_user_with_invalid_id(self, client, client_logged_in):
        client, user = client_logged_in

        # Create a PersonalInfo instance
        personal_info = PersonalInfoFactory(
            user_id_for_personal_info=user,
            api_user_id_for_cv="12345",
            api_id_of_cv="9999999",
        )

        # CREATE TOKENS FOR USER
        token_instance = TokensForUserFactory(user=user)

        # Simulate the delete request with an invalid id
        response = client.get(
            reverse(
                "cv_api:get_cv_to_delete",
                kwargs={"personal_info_id": personal_info.id + 11},
            ),
            HTTP_AUTHORIZATION=f"Bearer {token_instance.access_token}",
        )

        # Check the response status code
        assert response.status_code == 302

        # Check the response redirect URL
        assert response.url == "/"

        # Check the PersonalInfo instance status
        personal_info.refresh_from_db()
        assert personal_info.status == "FAILED"


@pytest.mark.django_db
class Test_WebHookEvent:

    @patch("json.loads")
    def test_cv_created(self, mock_json_loads, client, mock_relations_personal_info):

        # Create PersonalInfo instance for user
        personal_info = PersonalInfoFactory.create()

        # Mock the json data in webhook event
        data = {
            "event": "cv_created",
            "id": personal_info.api_id_of_cv,
            "user_id": personal_info.api_user_id_for_cv,
            "status": "CREATED",
        }
        mock_json_loads.return_value = data

        response = client.post(
            reverse("cv_api:cv-webhook"),
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert personal_info.api_id_of_cv == data["id"]
        assert personal_info.status == "CREATED"
        mock_json_loads.assert_called_once()

    @patch("json.loads")
    def test_cv_updated(self, mock_json_loads, client, mock_relations_personal_info):

        # Create PersonalInfo instance for user
        personal_info = PersonalInfoFactory.create()

        # Mock the json data in webhook event
        data = {
            "event": "cv_updated",
            "id": personal_info.api_id_of_cv,
            "user_id": personal_info.api_user_id_for_cv,
            "status": "UPDATED",
        }
        mock_json_loads.return_value = data

        response = client.post(
            reverse("cv_api:cv-webhook"),
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert personal_info.api_id_of_cv == data["id"]
        assert personal_info.status == "UPDATED"
        mock_json_loads.assert_called_once()

    @patch("json.loads")
    def test_cv_deleted(
        self,
        mock_json_loads,
        mock_personalinfo_delete,
        client_logged_in,
    ):
        client, user = client_logged_in

        personal_info = PersonalInfoFactory(user_id_for_personal_info=user)

        # # Mock the json data in webhook event
        data = {
            "event": "cv_deleted",
            "id": personal_info.api_id_of_cv,
            "user_id": personal_info.api_user_id_for_cv,
            "status": "DELETED",
        }

        mock_json_loads.return_value = data

        response = client.post(
            reverse("cv_api:cv-webhook"),
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        mock_json_loads.assert_called_once()
        mock_personalinfo_delete.assert_called_once()

    @patch("json.loads")
    def test_cv_deletion_failed(
        self, mock_json_loads, client, mock_relations_personal_info
    ):
        # Create PersonalInfo instance for user
        personal_info = PersonalInfoFactory.create()

        # Mock the json data in webhook event
        data = {
            "event": "cv_deletion_failed",
            "id": personal_info.api_id_of_cv,
            "user_id": personal_info.api_user_id_for_cv,
            "status": "FAILED",
        }
        mock_json_loads.return_value = data

        response = client.post(
            reverse("cv_api:cv-webhook"),
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        mock_json_loads.assert_called_once()
        assert personal_info.status == "FAILED"

    @patch("json.loads")
    def test_cv_update_failed(
        self, mock_json_loads, client, mock_relations_personal_info
    ):
        # Create PersonalInfo instance for user
        personal_info = PersonalInfoFactory.create()

        # Mock the json data in webhook event
        data = {
            "event": "cv_update_failed",
            "id": personal_info.api_id_of_cv,
            "user_id": personal_info.api_user_id_for_cv,
            "status": "FAILED",
        }
        mock_json_loads.return_value = data

        response = client.post(
            reverse("cv_api:cv-webhook"),
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        mock_json_loads.assert_called_once()
        assert personal_info.status == "FAILED"

    @patch("json.loads")
    def test_invalid_event_type(self, client, mock_json_loads):
        # Create PersonalInfo instance for user
        personal_info = PersonalInfoFactory.create()

        # Mock the json data in webhook event
        data = {
            "event": "invalid_event",
            "id": personal_info.api_id_of_cv,
            "user_id": personal_info.api_user_id_for_cv,
            "status": "FAILED",
        }
        mock_json_loads.return_value = data

        response = client.post(
            reverse("cv_api:cv-webhook"),
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 400
        mock_json_loads.assert_called_once()
        # Check if the response is an instance of JsonResponse
        assert isinstance(response, JsonResponse)


@pytest.mark.django_db
class Test_RetrieveCVDataToUpdate:
    def test_get_anonymous_user(self, client):

        personal_info_instance = PersonalInfoFactory()
        response = client.get(
            reverse(
                "cv_api:get_cv_to_update",
                kwargs={"personal_info_id": personal_info_instance.id},
            )
        )

        assert response.status_code == 302
        response.url == "/login/"

    def test_get_invalid_token(self, client_logged_in):
        # Create the user, and log-in this user
        client, user = client_logged_in

        personal_info_instance = PersonalInfoFactory(user_id_for_personal_info=user)

        with patch(
            "cv_api.views.RetrieveCVDataToUpdate.get_token_from_database",
            return_value=None,
        ):
            response = client.get(
                reverse(
                    "cv_api:get_cv_to_update",
                    kwargs={"personal_info_id": personal_info_instance.id},
                )
            )
            assert response.url == "/"
            assert response.status_code == 302

    def test_get_failure(self, client_logged_in):
        # create the user, log-in this user
        client, user = client_logged_in
        # create PersonalInfo instance
        personal_info_instance = PersonalInfoFactory(user_id_for_personal_info=user)

        with patch(
            "cv_api.views.RetrieveCVDataToUpdate.get_token_from_database",
            return_value="test_access_token",
        ):
            with patch("requests.get") as mock_get:
                mock_get.return_value.status_code = 404

                response = client.get(
                    reverse(
                        "cv_api:get_cv_to_update",
                        kwargs={"personal_info_id": personal_info_instance.id},
                    )
                )
                assert response.url == "/"
                assert response.status_code == 302
                # Access messages from the response
                messages = list(get_messages(response.wsgi_request))
                assert any(
                    "Something went wrong, Try again!" in str(message)
                    for message in messages
                )

    def test_get_success(self, client_logged_in, personal_info_data):
        # create user, log-in this user
        client, user = client_logged_in

        # create json data obtain from API
        data, instance, user = personal_info_data(user)

        # mock the data in "cv_data" cookie
        client.cookies["cv_data"] = data

        with patch(
            "cv_api.views.RetrieveCVDataToUpdate.get_token_from_database",
            return_value="test_access_token",
        ) as mock_tokens:

            with patch("requests.get") as mock_get:
                mock_get.return_value.status_code = 200
                mock_get.return_value.json.return_value = data

                response = client.get(
                    reverse(
                        "cv_api:get_cv_to_update",
                        kwargs={"personal_info_id": instance.id},
                    )
                )
                assert (
                    "cv_data" in response.wsgi_request.COOKIES and "cv_data" is not None
                )
                mock_get.assert_called_once()
                mock_tokens.assert_called_once_with(user.id)
                assert (
                    "cv_data" in response.wsgi_request.COOKIES
                    and response.wsgi_request.COOKIES["cv_data"] is not None
                )
                assert "cv_api.html" in (t.name for t in response.templates)
                for key in expected_keys:
                    assert (
                        key in response.context
                    ), f"{key} not found in response context"

    # def test_post_success(
    #     self,
    #     client_logged_in,
    #     personal_info_data,
    #     keys_adjusted_personal_info_data,
    #     data_to_post,
    # ):
    #     # create user, log-in this user
    #     client, user = client_logged_in

    #     # create json data obtain from API
    #     data, instance, user = personal_info_data(user)

    #     # get the data with keys adjusted in "data"
    #     data = keys_adjusted_personal_info_data(data)

    #     print(f"data-----{data}")

    #     # mock the data in "cv_data" cookie
    #     client.cookies["cv_data"] = json.dumps(data)

    #     with patch(
    #         "cv_api.views.RetrieveCVDataToUpdate.get_token_from_database",
    #         return_value="test_access_token",
    #     ):
    #         with patch("requests.patch") as mock_patch:
    #             mock_patch.return_value.status_code = 200
    #             mock_patch.return_value.json.return_value = {
    #                 "status": "UPDATED",
    #                 "id": instance.id,
    #                 "user_id": user.id,
    #             }

    #             data_to_post = data_to_post(data)

    #             # form = OverviewForm(data_to_post["overview_text"])
    #             # print(f"form erros------ :{ form.errors.as_data() }")

    #             response = client.post(
    #                 reverse(
    #                     "cv_api:get_cv_to_update",
    #                     kwargs={"personal_info_id": instance.id},
    #                 ),
    #                 data=data_to_post,
    #             )

    #             assert response.status_code == 302
    #             assert response.url == "/"
    #             mock_patch.assert_called_once()
