import pytest
from hunt.utilities import get_users_active_levels, get_user_level_for_level
from collections import Counter

pytestmark = pytest.mark.django_db
from factories import AnswerFactory, LevelFactory, HuntFactory, UserLevelFactory

def test_empty_active_levels(hunt, levels):
    assert len(get_users_active_levels(hunt)) == 0

def test_active_levels(hunt, levels):
    for level in levels:
        UserLevelFactory(hunt=hunt, level=level)

    active_levels = get_users_active_levels(hunt)
    assert len(active_levels) == 5
    assert sorted(active_levels) == [1,2,3,4,5]

def test_get_user_level(hunt, level):
    hunt2 = HuntFactory.create()
    UserLevelFactory.create(hunt=hunt, level=level)
    UserLevelFactory.create(hunt=hunt2, level=level)
    user_level = get_user_level_for_level(level, hunt.user)
    assert user_level.hunt == hunt
    user_level2 = get_user_level_for_level(level, hunt2.user)
    assert user_level2.hunt == hunt2
    assert user_level != user_level2
    with pytest.raises(RuntimeError):
        get_user_level_for_level(level, 'test')

