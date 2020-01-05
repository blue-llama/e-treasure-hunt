from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from hunt.models import Answer, Level
from hunt.forms import AnswerUploadForm, LevelUploadForm, BaseAnswerUploadForm
import pytest
import factory

from pytest_factoryboy import register
from factories import (
    AnswerFactory,
    HuntFactory,
    MultipleLevelFactory,
    LevelFactory,
    UserLevelFactory,
    MultiAnswerFactory,
    MultiLocationFactory,
    LocationFactory,
)
from collections import namedtuple

register(AnswerFactory)


@pytest.fixture(scope="function")
def user():
    return User.objects.create_user(username="test_user")


@pytest.fixture(scope="function")
def location():
    return LocationFactory.create()


@pytest.fixture(scope="function")
def answer():
    return AnswerFactory.create()


def build_answer_form_files():
    with open("tests/input/description.txt", "rb") as file:
        description = SimpleUploadedFile("description.txt", file.read())
    with open("tests/input/location.json", "rb") as file:
        info = SimpleUploadedFile("location.json", file.read())
    return {
        "description": description,
        "info": info,
    }

def build_base_answer_form_files():
    with open("tests/input/description.txt", "rb") as file:
        description = SimpleUploadedFile("description.txt", file.read())
    return {"description": description}


def build_answer_form_data():
    return {"name": "Answer name"}


@pytest.fixture(scope="function")
def answerform():
    answerform = AnswerUploadForm(
        data=build_answer_form_data(), files=build_answer_form_files()
    )
    answerform.is_valid()
    return answerform


@pytest.fixture(scope="function")
def baseanswerform():
    answerform = BaseAnswerUploadForm(
        data=build_answer_form_data(), files=build_base_answer_form_files()
    )
    answerform.is_valid()
    return answerform


def build_level_form_files():
    with open("tests/input/image.png", "rb") as file:
        image = SimpleUploadedFile("image.png", file.read())
    return {
        "clue": image,
        "hint1": image,
        "hint2": image,
        "hint3": image,
        "hint4": image,
    }


@pytest.fixture(scope="function")
def levelform():
    levelform = LevelUploadForm(data={"number": 1}, files=build_level_form_files())
    levelform.is_valid()
    return levelform


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

    # Create the levels
    MultipleLevelFactory.reset_sequence(1)
    levels = MultipleLevelFactory.create_batch(5)

    # Create the answers
    # 1 leads to 2, which leads to 3 and 4, which lead back to 5
    answers = []
    MultiLocationFactory.reset_sequence(1)
    answers.append(
        MultiAnswerFactory.create(solves_level=levels[0], leads_to_level=levels[1])
    )
    answers.append(
        MultiAnswerFactory.create(solves_level=levels[1], leads_to_level=levels[2])
    )
    answers.append(
        MultiAnswerFactory.create(solves_level=levels[1], leads_to_level=levels[3])
    )
    answers.append(
        MultiAnswerFactory.create(solves_level=levels[2], leads_to_level=levels[4])
    )
    # Answers 4 and 5 (which both lead to level 5 need the same location)
    answers.append(
        MultiAnswerFactory.create(
            solves_level=levels[3],
            leads_to_level=levels[4],
            location=LocationFactory(longitude=40, latitude=40),
        )
    )

    # Create the unlocked levels for this user
    user_levels = []
    for user_level in create_user_levels:
        user_levels.append(
            UserLevelFactory.create(hunt=hunt, level=levels[user_level - 1])
        )

    MultiLevelHunt = namedtuple("MutliLevelHunt", "hunt levels userlevels answers")
    return MultiLevelHunt(
        hunt=hunt, levels=levels, userlevels=user_levels, answers=answers
    )
