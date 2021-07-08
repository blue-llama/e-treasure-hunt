import pytest
import factory
import mock
from hunt.hint_mgr import create_answer, create_level, create_first_level
from hunt.models import Answer, Level
from hunt.forms import AnswerUploadForm
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
from uuid import uuid4
from factories import LevelFactory

pytestmark = pytest.mark.django_db

CLUE_NAME = str(uuid4()) + ".png"
SECOND_CLUE_NAME = str(uuid4()) + ".png"


def create_clue_names(clue):
    return str([clue for i in range(5)])


def test_create_answer(level, answerform):
    create_answer(level, answerform.cleaned_data)
    answer = Answer.objects.get(name="Answer name")
    assert answer.location.latitude == Decimal(10)
    assert answer.location.longitude == Decimal(100)
    assert answer.location.tolerance == 50
    assert answer.description == "Some text for a description"
    assert answer.name == "Answer name"
    assert level == answer.solves_level


def test_create_first_level(baseanswerform):
    create_first_level(baseanswerform.cleaned_data, baseanswerform.files)
    level = Level.objects.get(number=0)
    assert level
    assert level.clues == ""
    assert level.number == 0
    answer = Answer.objects.get(name="Answer name")
    assert answer.location.latitude == Decimal(0)
    assert answer.location.longitude == Decimal(0)
    assert answer.location.tolerance == 100
    assert answer.description == "Some text for a description"
    assert answer.name == "Answer name"
    assert level == answer.solves_level


@mock.patch("hunt.hint_mgr.create_file_thread", return_value=CLUE_NAME)
def test_create_level(mock, levelform):
    create_level(levelform.cleaned_data, levelform.files)
    level = Level.objects.get(number=1)
    assert level
    assert level.clues == create_clue_names(CLUE_NAME)


@mock.patch("hunt.hint_mgr.create_file_thread", return_value=SECOND_CLUE_NAME)
@mock.patch("hunt.hint_mgr.delete_old_clue_threads")
def test_create_existing_level(mock_create, mock_delete, levelform):
    LevelFactory.create(number=1, clues=create_clue_names(CLUE_NAME))
    create_level(levelform.cleaned_data, levelform.files)
    level = Level.objects.get(number=1)
    assert level.clues == create_clue_names(SECOND_CLUE_NAME)
