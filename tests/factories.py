from hunt.models import Answer, Level, HuntInfo, UserLevel, Location
from hunt.forms import AnswerUploadForm
from factory_djoy import CleanModelFactory, UserFactory
from decimal import Decimal
import factory

CLUE_NAME = "60bf0f67-14bd-488d-acdb-d677e9067515.png"


class LevelFactory(CleanModelFactory):
    class Meta:
        model = Level

    number = 1
    clues = str([CLUE_NAME for i in range(5)])


class MultipleLevelFactory(CleanModelFactory):
    class Meta:
        model = Level

    number = factory.Sequence(lambda n: n)
    clues = str([CLUE_NAME for i in range(5)])


class LocationFactory(CleanModelFactory):
    class Meta:
        model = Location

    longitude = "1.2345678"
    latitude = "-1.2345678"
    tolerance = 100


class AnswerFactory(CleanModelFactory):
    class Meta:
        model = Answer

    # These are decimal fields, so you can't pass a float, hence use the string
    name = "Test Name"
    description = "Test Description"
    location = factory.SubFactory(LocationFactory)
    solves_level = factory.SubFactory(LevelFactory)
    leads_to_level = factory.SubFactory(
        LevelFactory, number=2
    )  # Don't try and create the same level again so create a new one


class MultiLocationFactory(CleanModelFactory):
    class Meta:
        model = Location

    longitude = factory.Sequence(lambda n: n * 10)
    latitude = factory.Sequence(lambda n: n * 10)
    tolerance = 100


class MultiAnswerFactory(CleanModelFactory):
    class Meta:
        model = Answer

    # These are decimal fields, so you can't pass a float, hence use the string
    name = factory.Faker("name")
    description = factory.Faker("sentence", nb_words=10)
    location = factory.SubFactory(MultiLocationFactory)
    solves_level = factory.SubFactory(LevelFactory)
    leads_to_level = factory.SubFactory(
        LevelFactory, number=2
    )  # Don't try and create the same level again so create a new one


class HuntFactory(CleanModelFactory):
    class Meta:
        model = HuntInfo

    user = factory.SubFactory(UserFactory)


class UserLevelFactory(CleanModelFactory):
    class Meta:
        model = UserLevel

    hunt = factory.SubFactory(HuntFactory)
    level = factory.SubFactory(LevelFactory)
