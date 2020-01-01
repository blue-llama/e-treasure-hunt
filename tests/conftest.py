from django.contrib.auth.models import User
from hunt.models import Answer, Level
import pytest

from pytest_factoryboy import register
from factories import (
    AnswerFactory,
    HuntFactory,
    MultipleLevelFactory,
    LevelFactory,
    UserLevelFactory,
)

register(AnswerFactory)


@pytest.fixture(scope="function")
def user():
    return User.objects.create_user(username="test_user")


@pytest.fixture(scope="function")
def answer():
    return AnswerFactory.create()


@pytest.fixture(scope="function")
def hunt():
    return HuntFactory.create()


@pytest.fixture(scope="function")
def levels():
    MultipleLevelFactory.reset_sequence(1)
    return MultipleLevelFactory.create_batch(5)


@pytest.fixture(scope="function")
def level():
    return LevelFactory.create()


@pytest.fixture(scope="function")
def user_level():
    return UserLevelFactory.create()
