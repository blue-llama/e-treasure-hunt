import pytest
import mock
from hunt.hints import request_hint, release_level_hints
from hunt.models import UserLevel, HuntEvent
pytestmark = pytest.mark.django_db
from factories import UserLevelFactory, HuntFactory

def test_request_hint_no_level(rf):
    request = rf.get("/hint")
    assert request_hint(request) == "/oops"

def test_request_hint_on_non_active_level(rf, hunt, levels):
    UserLevelFactory.create(hunt=hunt, level=levels[0])
    request = rf.get("/hint", {'lvl': 2})
    request.user = hunt.user
    assert request_hint(request) == "/oops"

@mock.patch('hunt.hints.maybe_release_hints')
def test_request_hint(rf, hunt, levels):
    user_level = UserLevelFactory.create(hunt=hunt, level=levels[0])
    assert not user_level.hint_requested
    request = rf.get("/hint", {'lvl': 1})    
    request.user = hunt.user
    assert request_hint(request) == "/level/1"
    # Now we need to get the user_level object
    user_level = UserLevel.objects.get(hunt=hunt, level=levels[0])
    assert user_level.hint_requested
    assert len(HuntEvent.objects.all()) == 1

def test_release_level_hints(hunt, levels):
    hunt2 = HuntFactory.create()
    UserLevelFactory.create(hunt=hunt, level=levels[0], hint_requested=True, hints_shown=3)
    UserLevelFactory.create(hunt=hunt2, level=levels[0], hints_shown=3)
    release_level_hints()
    assert len(HuntEvent.objects.all()) == 1

    # Check we've increased the number of hints on the levels that were requested for hints
    user_level_with_hints = UserLevel.objects.get(hunt=hunt, level=levels[0])
    assert not user_level_with_hints.hint_requested
    assert user_level_with_hints.hints_shown == 4

    # Check we've not increased the number of hints on the levels that didn't have requests
    user_level_without_hints = UserLevel.objects.get(hunt=hunt2, level=levels[0])
    assert not user_level_without_hints.hint_requested
    assert user_level_without_hints.hints_shown == 3
