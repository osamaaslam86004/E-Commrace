# conftest.py

import logging

import celery
import celery.contrib
import celery.contrib.pytest
import pytest

pytest_plugins = "celery.contrib.pytest"


@pytest.fixture(scope="session")
def celery_config():
    return {
        "broker_url": "redis://localhost:6379/0",  # Redis as broker
        "result_backend": "redis://localhost:6379/0",  # Redis as result backend
        "task_always_eager": False,  # Ensure tasks are executed by the worker
        "accept_content": ["json"],
        "task_serializer": "json",
        "result_serializer": "json",
    }


# @pytest.fixture(scope="session")
# def celery_worker_parameters():
#     return {"concurrency": 1}


@pytest.fixture(scope="session")
def celery_enable_logging():
    return True


# Disable Faker and Factory Boy DEBUG logging globally
faker_logger = logging.getLogger("faker")
factory_logger = logging.getLogger("factory")

faker_logger.setLevel(logging.ERROR)
factory_logger.setLevel(logging.ERROR)


@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    faker_logger.setLevel(logging.ERROR)
    factory_logger.setLevel(logging.ERROR)


# @pytest.fixture(scope="session", autouse=True)
# def configure_django_settings():
#     settings.SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
#     settings.SESSION_COOKIE_SECURE = False  # For testing without HTTPS
#     settings.SESSION_COOKIE_HTTPONLY = True
#     settings.SESSION_COOKIE_AGE = 3600  # Optional: Set cookie session duration

#     return settings
