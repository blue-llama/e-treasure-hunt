from hunt.levels import (
    is_correct_answer,
    update_active_levels,
    get_users_active_levels,
    advance_level,
    log_level_advance,
    create_new_user_level,
    look_for_answers,
    can_request_hint,
    get_level_numbers,
    get_answer_for_last_level,
    get_hints_to_show,
)
from hunt.models import HuntEvent, UserLevel
import pytest
import mock
from factory_djoy import UserFactory
from storages.backends.dropbox import DropBoxStorage

pytestmark = pytest.mark.django_db
from factories import AnswerFactory, UserLevelFactory, HuntFactory, CLUE_NAME


def test_correct_answer(location):
    assert is_correct_answer(-1.2345678, 1.2345678, location)


def test_incorrect_answer(location):
    assert not is_correct_answer(1, -1, location)
    assert not is_correct_answer(1.2345678, 180 - 1.2345678, location)


def test_update_active_levels(hunt, levels):
    # Create a hunt with only 1 active level
    UserLevelFactory.create(hunt=hunt, level=levels[0])
    assert len(hunt.active_levels.all()) == 1
    # Create an answer for the first level
    answer = AnswerFactory.create(solves_level=levels[0], leads_to_level=levels[1])
    update_active_levels(hunt, answer)

    # We should now have 2 active levels, numbered 1 and 2
    assert len(hunt.active_levels.all()) == 2
    active_levels = get_users_active_levels(hunt)
    assert active_levels == [2, 1]


def test_advance_level(hunt, levels):
    UserLevelFactory.create(hunt=hunt, level=levels[0])
    answer = AnswerFactory.create(solves_level=levels[0], leads_to_level=levels[1])
    advance_level(hunt, answer)

    # We should now have 2 active levels, numbered 1 and 2
    assert len(hunt.active_levels.all()) == 2
    active_levels = get_users_active_levels(hunt)
    assert active_levels == [2, 1]


def test_log_level_advance(hunt, answer):
    log_level_advance(hunt, answer)
    assert len(HuntEvent.objects.all()) == 1


def test_create_new_user_level(hunt, level):
    assert len(UserLevel.objects.all()) == 0
    create_new_user_level(hunt, level)
    assert len(UserLevel.objects.all()) == 1
    assert UserLevel.objects.get(hunt=hunt, level=level)


def test_can_request_hint_hint_requested(user_level):
    user_level.hint_requested = True
    hint_allowed, reason = can_request_hint(user_level)
    assert not hint_allowed
    assert reason == "Your team has already requested a hint."


def test_can_request_hint_hint_requested(user_level):
    user_level.hints_shown = 5
    hint_allowed, reason = can_request_hint(user_level)
    assert not hint_allowed
    assert reason == "No more hints are available on this level."


def test_can_request_hint(user_level):
    hint_allowed, reason = can_request_hint(user_level)
    assert hint_allowed
    assert reason == ""


def test_get_level_numbers(rf, hunt, levels):
    """ 
    Test that a normal user can only get the levels available to them but staff can access all levels.
    """
    UserLevelFactory.create(hunt=hunt, level=levels[0])
    UserLevelFactory.create(hunt=hunt, level=levels[1])
    request = rf.get("/level/1")
    request.user = hunt.user
    assert get_level_numbers(request) == [2, 1]
    staff_user = UserFactory.create(is_staff=True)
    request = rf.get("/level/1")
    request.user = staff_user
    assert get_level_numbers(request) == [5, 4, 3, 2, 1]


@mock.patch("hunt.levels.is_correct_answer", return_value=True)
def test_look_for_answers(mock, rf, hunt, levels):
    request = rf.get("/do-search?lat=1.0&long=1.0")
    request.user = hunt.user
    UserLevelFactory.create(hunt=hunt, level=levels[0])
    answer = AnswerFactory.create(solves_level=levels[0], leads_to_level=levels[1])
    assert look_for_answers(request) == "/level/" + str(levels[1].number)


@mock.patch("hunt.levels.is_correct_answer", return_value=False)
def test_look_for_answers_incorrect_answer(mock, hunt, rf):
    request = rf.get("/do-search?lat=1.0&long=1.0")
    request.user = hunt.user
    assert look_for_answers(request) == "/nothing-here"


def test_get_answer_for_last_level(hunt, levels):
    answer = AnswerFactory.create(solves_level=levels[0], leads_to_level=levels[1])
    assert get_answer_for_last_level(levels[1].number) == answer


def url_side_effect(url):
    return url

@mock.patch('storages.backends.dropbox.DropBoxStorage.url', side_effect=url_side_effect)
def test_get_hints_to_show(mock, hunt, level):
    userlevel = UserLevelFactory.create(hunt=hunt, level=level, hints_shown=3)
    assert get_hints_to_show(level, userlevel) == [CLUE_NAME for i in range(3)]

