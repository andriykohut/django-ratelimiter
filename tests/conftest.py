import pytest
from rest_framework.test import APIClient


@pytest.fixture
def drf_client() -> APIClient:
    return APIClient()
