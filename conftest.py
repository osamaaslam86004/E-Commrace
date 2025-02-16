# conftest.py

import pytest
from django.test import Client


@pytest.fixture(scope="module")
def client():
    return Client()
