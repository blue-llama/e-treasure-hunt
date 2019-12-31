from hunt.models import Answer, Level, HuntInfo, UserLevel
from factory_djoy import CleanModelFactory, UserFactory
from decimal import Decimal
import factory

class LevelFactory(CleanModelFactory):
    class Meta:
        model = Level

    number = 1
    name = "Test Name"
    clues = "Test Clues"

class MultipleLevelFactory(CleanModelFactory):
    class Meta:
        model = Level

    number = factory.Sequence(lambda n: n)
    name = "Test Name"
    clues = "Test Clues"

class AnswerFactory(CleanModelFactory):
    class Meta:
        model = Answer

    # These are decimal fields, so you can't pass a float, hence use the string
    longitude = "1.2345678"
    latitude = "-1.2345678"
    tolerance = 100
    description = "Test Description"
    for_level = factory.SubFactory(LevelFactory)
    next_level = factory.SubFactory(LevelFactory, number=2) # Don't try and create the same level again so create a new one

class HuntFactory(CleanModelFactory):
    class Meta:
        model = HuntInfo

    user = factory.SubFactory(UserFactory)

class UserLevelFactory(CleanModelFactory):
    class Meta:
        model = UserLevel
    
    hunt = factory.SubFactory(HuntFactory)
    level = factory.SubFactory(LevelFactory)



