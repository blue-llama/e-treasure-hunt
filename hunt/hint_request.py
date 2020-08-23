"""
Functions for requesting hints.
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.http.request import HttpRequest
from django.utils import timezone

import hunt.slack as slack
from hunt.constants import HINTS_PER_LEVEL
from hunt.models import HuntEvent, HuntInfo

# Time in minutes to wait for a hint to be dropped after a request.
LEADER_HINT_WAIT_TIME = 40
NON_LEADER_HINT_WAIT_TIME = 20


def request_hint(request: HttpRequest) -> str:
    # Request must be for a specific level.
    lvl = request.GET.get("lvl")
    if lvl is None:
        return "/oops"

    # Check that this a request for the user's current level.
    hunt_info = request.user.huntinfo
    if int(lvl) != hunt_info.level:
        return "/oops"

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
    event.team = request.user.username
    event.level = lvl
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
    delay = 20 * hunt_info.hints_shown

    # The leading two teams are made to wait a bit longer.
    hunts = HuntInfo.objects.filter(user__is_staff=False).order_by(
        "-level", "-hints_shown"
    )
    if len(hunts) > 1:
        second = hunts[1]
        second_place = (second.level, second.hints_shown)
        user_place = (hunt_info.level, hunt_info.hints_shown)
        if user_place >= second_place:
            delay += 20

    return delay


def prepare_next_hint(hunt_info: HuntInfo) -> None:
    """
    Prepare to release the next hint, by calculating when it will become available.
    """
    # Don't try to release more hints than there are.
    if hunt_info.hints_shown >= HINTS_PER_LEVEL:
        return

    # Calculate when to release the next hint.
    now = timezone.now()
    delay = determine_hint_delay(hunt_info)
    hunt_info.next_hint_release = now + timedelta(minutes=delay)
    hunt_info.save()

    # If we have a slack channel for this user, schedule an announcement to coincide
    # with the hint becoming available.
    if hunt_info.slack_channel:
        timestamp = int(hunt_info.next_hint_release.timestamp())
        slack.schedule_hint_announcement(hunt_info.slack_channel, timestamp)


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
        event.team = user.username
        event.type = HuntEvent.HINT_REL
        event.level = hunt_info.level
        event.save()

        # Release this hint.
        hunt_info.hints_shown += 1
        hunt_info.hint_requested = False
        hunt_info.next_hint_release = None
        hunt_info.save()
