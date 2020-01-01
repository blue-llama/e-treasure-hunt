from hunt.models import Answer, Level, HuntInfo, UserLevel
from factory_djoy import CleanModelFactory, UserFactory
from decimal import Decimal
import factory


class LevelFactory(CleanModelFactory):
    class Meta:
        model = Level

    number = 1
    clues = "Test Clues"


class MultipleLevelFactory(CleanModelFactory):
    class Meta:
        model = Level

    number = factory.Sequence(lambda n: n)
    clues = "Test Clues"


class AnswerFactory(CleanModelFactory):
    class Meta:
        model = Answer

    # These are decimal fields, so you can't pass a float, hence use the string
    longitude = "1.2345678"
    latitude = "-1.2345678"
    tolerance = 100
    name = "Test Name"
    description = "Test Description"
    solves_level = factory.SubFactory(LevelFactory)
    leads_to_level = factory.SubFactory(
        LevelFactory, number=2
    )  # Don't try and create the same level again so create a new one


class MultiAnswerFactory(CleanModelFactory):
    class Meta:
        model = Answer

    # These are decimal fields, so you can't pass a float, hence use the string
    longitude = factory.Sequence(lambda n: n * 10)
    latitude = factory.Sequence(lambda n: n * 10)
    tolerance = 100
    name = factory.Faker("name")
    description = factory.Faker("sentence", nb_words=10)
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
