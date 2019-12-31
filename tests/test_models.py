from hunt.models import HuntInfo
import pytest

pytestmark = pytest.mark.django_db
from factories import AnswerFactory, LevelFactory
def test_create_hunt_info(hunt):
	assert len(HuntInfo.objects.all()) == 1

def test_valid_answer():
	assert AnswerFactory.create()

def test_invalid_answer():
	# Longitude and Latitude use the DecimalField so use strings instead of floats
	with pytest.raises(RuntimeError):
		AnswerFactory.create(longitude="1.23456789")
	with pytest.raises(RuntimeError):
		AnswerFactory.create(latitude="1.23456789")
	with pytest.raises(RuntimeError):
		AnswerFactory.create(latitude="90.1")
	with pytest.raises(RuntimeError):
		AnswerFactory.create(latitude="-90.1")
	with pytest.raises(RuntimeError):
		AnswerFactory.create(longitude="180.1")
	with pytest.raises(RuntimeError):
		AnswerFactory.create(longitude="-180.1")
	with pytest.raises(RuntimeError):
		AnswerFactory.create(tolerance=10001)

def test_valid_level():
	assert LevelFactory.create()

def test_cant_create_multiple_same_level():
	LevelFactory.create()
	with pytest.raises(RuntimeError):
		LevelFactory.create()

def test_create_multiple_levels():
	LevelFactory.create()
	assert LevelFactory.create(number=2)