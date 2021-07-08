import pytest
import mock
from hunt.hints import request_hint, release_level_hints, log_hint_request
from hunt.models import UserLevel, HuntEvent

pytestmark = pytest.mark.django_db
from factories import UserLevelFactory, HuntFactory


def test_request_hint_no_level(rf):
    request = rf.get("/hint")
    assert request_hint(request) == "/oops"


def test_request_hint_on_non_active_level(rf, hunt, levels):
    UserLevelFactory.create(hunt=hunt, level=levels[0])
    request = rf.get("/hint", {"lvl": 2})
    request.user = hunt.user
    assert request_hint(request) == "/oops"


def test_log_hint_event(rf, hunt):
    request = rf.get("/hint", {"lvl": 5})
    request.user = hunt.user
    log_hint_request(request, request.GET.get("lvl", None))
    assert len(HuntEvent.objects.all()) == 1
    assert len(HuntEvent.objects.filter(type="REQ")) == 1


@mock.patch("hunt.hints.maybe_release_hints")
def test_request_hint(mock, rf, hunt, levels):
    user_level = UserLevelFactory.create(hunt=hunt, level=levels[0])
    assert not user_level.hint_requested
    request = rf.get("/hint", {"lvl": 1})
    request.user = hunt.user
    assert request_hint(request) == "/level/1"
    # Now we need to get the user_level object
    user_level = UserLevel.objects.get(hunt=hunt, level=levels[0])
    assert user_level.hint_requested
    assert len(HuntEvent.objects.all()) == 1


def test_release_level_hints(hunt, levels):
    hunt2 = HuntFactory.create()
    UserLevelFactory.create(
        hunt=hunt, level=levels[0], hint_requested=True, hints_shown=3
    )
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


@pytest.mark.parametrize("create_user_levels", [[1, 2, 4]])
def test_release_level_hints_multiple_requested(multi_level_hunt):
    hunt = multi_level_hunt.hunt
    user_levels = multi_level_hunt.userlevels
    levels = multi_level_hunt.levels
    user_levels[0].hints_shown = 3
    user_levels[0].save()
    user_levels[1].hints_shown = 2
    user_levels[1].hint_requested = True
    user_levels[1].save()
    user_levels[2].hints_shown = 4
    user_levels[2].hint_requested = True
    user_levels[2].save()
    hunt2 = HuntFactory.create()
    UserLevelFactory.create(hunt=hunt2, level=levels[0], hints_shown=3)
    UserLevelFactory.create(
        hunt=hunt2, level=levels[1], hint_requested=True, hints_shown=3
    )
    UserLevelFactory.create(
        hunt=hunt2, level=levels[2], hint_requested=True, hints_shown=2
    )
    release_level_hints()
    # We've released 4 hints
    assert len(HuntEvent.objects.all()) == 4

    user_level = UserLevel.objects.get(hunt=hunt, level=levels[0])
    assert user_level.hints_shown == 3

    user_level = UserLevel.objects.get(hunt=hunt, level=levels[1])
    assert not user_level.hint_requested
    assert user_level.hints_shown == 3

    user_level = UserLevel.objects.get(hunt=hunt, level=levels[3])
    assert not user_level.hint_requested
    assert user_level.hints_shown == 5

    # The other user's first level
    user_level = UserLevel.objects.get(hunt=hunt2, level=levels[0])
    assert user_level.hints_shown == 3

    user_level = UserLevel.objects.get(hunt=hunt2, level=levels[1])
    assert not user_level.hint_requested
    assert user_level.hints_shown == 4

    user_level = UserLevel.objects.get(hunt=hunt2, level=levels[2])
    assert not user_level.hint_requested
    assert user_level.hints_shown == 3
