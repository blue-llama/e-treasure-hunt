from hunt.levels import is_correct_answer, update_active_levels, get_users_active_levels, advance_level, clear_private_hints
import pytest
pytestmark = pytest.mark.django_db
from factories import AnswerFactory, UserLevelFactory, HuntFactory

def test_correct_answer(answer):
    assert is_correct_answer(-1.2345678, 1.2345678, answer)

def test_incorrect_answer(answer):
    assert not is_correct_answer(1, -1, answer)
    assert not is_correct_answer(1.2345678, 180 - 1.2345678, answer)

def test_update_active_levels(hunt, levels):
    # Create a hunt with only 1 active level
    UserLevelFactory.create(hunt=hunt, level=levels[0])
    assert len(hunt.active_levels.all()) == 1
    # Create an answer for the first level
    answer = AnswerFactory.create(for_level=levels[0], next_level=levels[1])
    update_active_levels(hunt, answer)

    # We should now have 2 active levels, numbered 1 and 2
    assert len(hunt.active_levels.all()) == 2
    active_levels = get_users_active_levels(hunt)
    assert sorted(active_levels) == [1,2]

def test_clear_private_hint(levels):
    hunt = HuntFactory(private_hint_requested=True, private_hints_shown=3)
    clear_private_hints(hunt)
    assert not hunt.private_hint_requested
    assert hunt.private_hints_shown == 0

def test_advance_level(hunt, levels):
    UserLevelFactory.create(hunt=hunt, level=levels[0])
    answer = AnswerFactory.create(for_level=levels[0], next_level=levels[1])
    advance_level(hunt, answer)

    # We should now have 2 active levels, numbered 1 and 2
    assert len(hunt.active_levels.all()) == 2
    active_levels = get_users_active_levels(hunt)
    assert sorted(active_levels) == [1,2]
