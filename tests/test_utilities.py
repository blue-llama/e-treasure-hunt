import pytest
from hunt.utilities import get_users_active_levels, get_user_level_for_level
from collections import Counter

pytestmark = pytest.mark.django_db
from factories import AnswerFactory, LevelFactory, HuntFactory, UserLevelFactory

def test_empty_active_levels():
	hunt = HuntFactory()
	levels = []
	for ii in range(1,5):
		level = LevelFactory(number=ii)
		levels.append(level)

	assert len(get_users_active_levels(hunt)) == 0

def test_active_levels():
	hunt = HuntFactory()
	levels = []
	for ii in range(1,6):
		level = LevelFactory(number=ii)
		levels.append(level)
		UserLevelFactory(hunt=hunt, level=level)

	active_levels = get_users_active_levels(hunt)
	assert len(active_levels) == 5
	assert sorted(active_levels) == [1,2,3,4,5]

def test_get_user_level():
	hunt = HuntFactory()
	hunt2 = HuntFactory()
	level = LevelFactory()
	UserLevelFactory(hunt=hunt, level=level)
	UserLevelFactory(hunt=hunt2, level=level)
	user_level = get_user_level_for_level(level, hunt.user)
	assert user_level.hunt == hunt
	user_level2 = get_user_level_for_level(level, hunt2.user)
	assert user_level2.hunt == hunt2
	assert user_level != user_level2
	with pytest.raises(Exception):
		get_user_level_for_level(level, 'test')

