"""
Functions for releasing hints.
"""

from django.contrib.auth.models import User
from django.utils import timezone

from hunt.models import HuntEvent, HuntInfo


def maybe_release_hint(user: User) -> None:
    """
    Release any requested hint that has been delayed for the appropriate
    length of time.
    """
    hunt_info = user.huntinfo
    if check_hint_release(hunt_info):
        event = HuntEvent()
        event.time = timezone.now()
        event.team = user.username
        event.type = HuntEvent.HINT_REL
        event.level = hunt_info.level
        event.save()

        release_hint(hunt_info)


def check_hint_release(hunt_info: HuntInfo) -> bool:
    """
    Check whether we've passed the threshold to release the next hint.
    """
    time_now = timezone.now()
    return (
        hunt_info.hint_requested
        and hunt_info.next_hint_release is not None
        and time_now > hunt_info.next_hint_release
    )


def release_hint(hunt_info: HuntInfo) -> None:
    """
    Updates the HuntInfo object to take into account that a hint has been released.
    """
    hunt_info.hints_shown += 1
    hunt_info.hint_requested = False
    hunt_info.next_hint_release = None
    hunt_info.save()
