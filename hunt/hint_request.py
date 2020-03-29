"""
Functions for requesting hints.
"""
from datetime import datetime, timedelta

from django.http.request import HttpRequest

import hunt.slack as slack
from hunt.models import HuntEvent, HuntInfo

# Time in minutes to wait for a hint to be dropped after a request.
LEADER_HINT_WAIT_TIME = 40
NON_LEADER_HINT_WAIT_TIME = 20


def request_hint(request: HttpRequest) -> str:
    # Request must be for a specific level - not allowed to request hints for old
    # levels.
    lvl = request.GET.get("lvl")
    if lvl is None:
        return "oops"

    # Check that this a request for the user's current level.
    lvl = int(lvl)
    hunt_info = request.user.huntinfo
    if lvl != hunt_info.level:
        return "/oops"

    # If a hint request is already in progress, there's nothing to do here.
    # Just send the user back to the level they're on.
    if hunt_info.hint_requested:
        return "/level/" + str(lvl)

    # Log an event to say there's been a hint request.
    event = HuntEvent()
    event.time = datetime.utcnow()
    event.type = HuntEvent.HINT_REQ
    event.team = request.user.username
    event.level = lvl
    event.save()

    process_hint_request(hunt_info)

    # If we have a slack channel for this user, schedule an announcement to coincide
    # with the hint release.
    if hunt_info.slack_channel:
        timestamp = int(hunt_info.next_hint_release.timestamp())
        slack.schedule_hint_announcement(hunt_info.slack_channel, timestamp)

    # Redirect back to the level in question.
    return "/level/" + str(lvl)


def get_furthest_active_level() -> int:
    """
    Finds the furthest level anyone has reached in the hunt.
    """
    hunts = HuntInfo.objects.all()
    return max(hunt.level for hunt in hunts if not hunt.user.is_staff)


def in_the_lead(hunt_info: HuntInfo) -> bool:
    """
    A user is in the lead if they are at the furthest active level
    anyone has reached and have received the most (or joint most)
    hints for that level.
    """
    if hunt_info.level < get_furthest_active_level():
        return False

    hunts = HuntInfo.objects.filter(level=hunt_info.level)
    max_hints = max(hunt.hints_shown for hunt in hunts if not hunt.user.is_staff)
    return hunt_info.hints_shown == max_hints


def determine_hint_delay(hunt_info: HuntInfo) -> int:
    """
    Determine how long a user has to wait before seeing the next
    hint. Users who are in the lead have to wait longer than others.
    """
    if in_the_lead(hunt_info):
        return LEADER_HINT_WAIT_TIME

    return NON_LEADER_HINT_WAIT_TIME


def process_hint_request(hunt_info: HuntInfo) -> None:
    """
    Sets fields on the HuntInfo to indicate that a hint request is in
    progress.
    """
    delay = determine_hint_delay(hunt_info)
    hunt_info.hint_requested = True
    hunt_info.next_hint_release = datetime.now() + timedelta(minutes=delay)
    hunt_info.save()
