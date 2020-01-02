import pytest
import factory
from hunt.hint_mgr import create_answer
from hunt.models import Answer
from hunt.forms import AnswerForm
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile

pytestmark = pytest.mark.django_db

def test_create_answer(level, answerform):
    create_answer(level, answerform.cleaned_data)
    answer = Answer.objects.get(name="Answer name")
    assert answer.location.latitude == Decimal(10)
    assert answer.location.longitude == Decimal(100)
    assert answer.location.tolerance == 50
    answer.clean()