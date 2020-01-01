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
    MultiAnswerFactory
)
from collections import namedtuple

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

@pytest.fixture(scope="function")
def multi_level_hunt(create_user_levels):
    # Create a hunt
    hunt = HuntFactory.create()

    # Create 
    MultipleLevelFactory.reset_sequence(1)
    levels = MultipleLevelFactory.create_batch(5)

    # The user is on the first level
    user_levels = []
    for user_level in create_user_levels:
        user_levels.append(UserLevelFactory.create(hunt=hunt, level=levels[user_level-1]))

    # 1 leads to 2, which leads to 3 and 4, which lead back to 5
    answers = []
    MultiAnswerFactory.reset_sequence(1)
    answers.append(MultiAnswerFactory.create(solves_level=levels[0], leads_to_level=levels[1]))
    answers.append(MultiAnswerFactory.create(solves_level=levels[1], leads_to_level=levels[2]))
    answers.append(MultiAnswerFactory.create(solves_level=levels[1], leads_to_level=levels[3]))
    answers.append(MultiAnswerFactory.create(solves_level=levels[2], leads_to_level=levels[4]))
    answers.append(MultiAnswerFactory.create(solves_level=levels[3], leads_to_level=levels[4], longitude=40, latitude=40))

    MultiLevelHunt = namedtuple('MutliLevelHunt', 'hunt levels userlevels answers')
    return MultiLevelHunt(hunt=hunt, levels=levels, userlevels=user_levels, answers=answers)
