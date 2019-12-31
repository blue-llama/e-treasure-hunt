from hunt.models import Answer, Level
from factory_djoy import CleanModelFactory
from decimal import Decimal
import factory

class LevelFactory(CleanModelFactory):
	class Meta:
		model = Level

	number = 1
	name = "Test Name"
	description = "Test Description"
	clues = "Test Clues"

class AnswerFactory(CleanModelFactory):
	class Meta:
		model = Answer

	# These are decimal fields, so you can't pass a float, hence use the string
	longitude = "1.2345678"
	latitude = "-1.2345678"
	tolerance = "100"
	for_level = factory.SubFactory(LevelFactory)
	next_level = factory.SubFactory(LevelFactory, number=2)

