from django.contrib.auth.models import User
from hunt.models import Answer, Level
import pytest

@pytest.fixture(scope="function")
def user():
	return User.objects.create_user(username="test_user")

@pytest.fixture(scope="function")
def answer():
	return Answer.objects.create(latitude=1.2345678, longitude=-1.2345678, tolerance=100)