"""
Functions for requesting hints.
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from hunt.constants import HINTS_PER_LEVEL
from hunt.models import HuntEvent, HuntInfo
from hunt.utils import AuthenticatedHttpRequest, max_level


def request_hint(request: AuthenticatedHttpRequest) -> str:
    hunt_info = request.user.huntinfo

    # Check that this is a request for the user's current level.
    lvl = request.GET.get("lvl")
    if lvl is None:
        return "/oops"

    if int(lvl) != hunt_info.level:
        return "/oops"

    # Check that this request is for the expected hint.
    hint = request.GET.get("hint")
    if hint is None:
        return "/oops"

    if int(hint) != hunt_info.hints_shown:
        return "/level/" + lvl

    # Prevent requesting more hints than there are.
    if hunt_info.hints_shown >= HINTS_PER_LEVEL:
        return "/oops"

    # If a hint request is already in progress, there's nothing to do here.
    # Just send the user back to the level they're on.
    if hunt_info.hint_requested:
        return "/level/" + lvl

    # Log an event to say there's been a hint request.
    event = HuntEvent()
    event.time = timezone.now()
    event.type = HuntEvent.HINT_REQ
    event.user = request.user
    event.level = hunt_info.level
    event.save()

    # Record that a hint has been requested.
    hunt_info.hint_requested = True
    hunt_info.save()

    # Redirect back to the level in question.
    return "/level/" + lvl


def determine_hint_delay(hunt_info: HuntInfo) -> int:
    """
    Determine how long a user has to wait before seeing the next hint, in minutes.
    """
    # Default to 30 minutes, tweak according to the team's position in the race:
    #
    # - leaders get a ten minute extra delay
    # - outright last place gets a ten minute reduction.
    delay = 30

    hunts = HuntInfo.objects.filter(user__is_staff=False).order_by(
        "-level", "-hints_shown"
    )
    count = len(hunts)
    if count > 1:
        user_place = (hunt_info.level, hunt_info.hints_shown)
        if user_place == (hunts[0].level, hunts[0].hints_shown):
            delay += 10
        elif user_place < (hunts[count - 2].level, hunts[count - 2].hints_shown):
            delay -= 10

    return delay


def prepare_next_hint(hunt_info: HuntInfo) -> None:
    """
    Prepare to release the next hint, by calculating when it will become available.
    """
    # Don't try to release more hints than there are.
    if hunt_info.hints_shown >= HINTS_PER_LEVEL:
        return

    # Don't try to release hints on the last level.
    if hunt_info.level >= max_level():
        return

    # Calculate when to release the next hint.
    now = timezone.now()
    delay = determine_hint_delay(hunt_info)
    hunt_info.next_hint_release = now + timedelta(minutes=delay)
    hunt_info.save()


def maybe_release_hint(user: User) -> None:
    """
    Release any requested hint that has been delayed for the appropriate length of time.
    """
    hunt_info = user.huntinfo
    now = timezone.now()
    if (
        hunt_info.hint_requested
        and hunt_info.next_hint_release is not None
        and now > hunt_info.next_hint_release
    ):
        # Record the event.
        event = HuntEvent()
        event.time = now
        event.user = user
        event.type = HuntEvent.HINT_REL
        event.level = hunt_info.level
        event.save()

        # Release this hint.
        hunt_info.hints_shown += 1
        hunt_info.hint_requested = False
        hunt_info.next_hint_release = None
        hunt_info.save()
