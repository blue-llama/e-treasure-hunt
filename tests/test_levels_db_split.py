from hunt.levels import (
    get_users_active_levels,
    look_for_answers,
    can_request_hint,
    get_level_numbers,
    get_answer_for_last_level,
)
from hunt.models import HuntEvent, UserLevel
import pytest
import mock
from factory_djoy import UserFactory

pytestmark = pytest.mark.django_db
from factories import AnswerFactory, UserLevelFactory, HuntFactory

SINGLE_LEVEL = [[1]]
LEVEL_ONE_AND_TWO = [[1, 2]]
HALF_OF_SPLIT_LEVEL = [[1, 2, 3], [1, 2, 4]]


@pytest.mark.parametrize("create_user_levels", SINGLE_LEVEL)
def test_look_for_answers_no_correct_answer(rf, multi_level_hunt):
    hunt = multi_level_hunt.hunt
    request = rf.get("/do-search?lat=1.0&long=1.0")
    request.user = hunt.user
    assert look_for_answers(request) == "/nothing-here"


@pytest.mark.parametrize("create_user_levels", SINGLE_LEVEL)
def test_look_for_answers_answer_to_unavailable_level(rf, multi_level_hunt):
    hunt = multi_level_hunt.hunt
    request = rf.get("/do-search?lat=20.0&long=20.0")
    request.user = hunt.user
    assert look_for_answers(request) == "/nothing-here"


@pytest.mark.parametrize("create_user_levels", SINGLE_LEVEL)
def test_look_for_answers_answer(rf, multi_level_hunt):
    hunt = multi_level_hunt.hunt
    request = rf.get("/do-search?lat=10.0&long=10.0")
    request.user = hunt.user
    assert look_for_answers(request) == "/level/2"
    # There are now 2 active levels
    assert get_users_active_levels(hunt) == [2, 1]
    assert len(UserLevel.objects.all()) == 2
    assert len(HuntEvent.objects.all()) == 1


@pytest.mark.parametrize("create_user_levels", LEVEL_ONE_AND_TWO)
def test_look_for_answers_second_answer(rf, multi_level_hunt):
    hunt = multi_level_hunt.hunt
    # We've unlocked the first 2 levels
    request = rf.get("/do-search?lat=30.0&long=30.0")
    request.user = hunt.user
    assert look_for_answers(request) == "/level/4"
    # There are now 2 active levels
    assert get_users_active_levels(hunt) == [4, 2, 1]
    assert len(UserLevel.objects.all()) == 3
    assert len(HuntEvent.objects.all()) == 1


@pytest.mark.parametrize("create_user_levels", LEVEL_ONE_AND_TWO)
def test_look_for_answers_first_answer(rf, multi_level_hunt):
    hunt = multi_level_hunt.hunt
    # We've unlocked the first 2 levels
    request = rf.get("/do-search?lat=20.0&long=20.0")
    request.user = hunt.user
    assert look_for_answers(request) == "/level/3"
    # There are now 2 active levels
    assert get_users_active_levels(hunt) == [3, 2, 1]
    assert len(UserLevel.objects.all()) == 3
    assert len(HuntEvent.objects.all()) == 1


@pytest.mark.parametrize("create_user_levels", LEVEL_ONE_AND_TWO)
def test_look_for_answers_answer_both(rf, multi_level_hunt):
    hunt = multi_level_hunt.hunt
    request = rf.get("/do-search?lat=30.0&long=30.0")
    request.user = hunt.user
    assert look_for_answers(request) == "/level/4"
    request = rf.get("/do-search?lat=20.0&long=20.0")
    request.user = hunt.user
    assert look_for_answers(request) == "/level/3"
    assert get_users_active_levels(hunt) == [4, 3, 2, 1]
    assert len(UserLevel.objects.all()) == 4
    assert len(HuntEvent.objects.all()) == 2


@pytest.mark.parametrize("create_user_levels", HALF_OF_SPLIT_LEVEL)
def test_look_for_answers_skip_split_level(rf, multi_level_hunt, create_user_levels):
    hunt = multi_level_hunt.hunt
    assert len(multi_level_hunt.userlevels) == 3
    request = rf.get("/do-search?lat=40.0&long=40.0")
    request.user = hunt.user
    expected_levels = create_user_levels.copy()
    expected_levels.append(5)
    assert look_for_answers(request) == "/level/5"
    assert get_users_active_levels(hunt) == sorted(expected_levels, reverse=True)
    assert len(UserLevel.objects.all()) == 4
    assert len(HuntEvent.objects.all()) == 1
