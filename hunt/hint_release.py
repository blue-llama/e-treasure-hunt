"""
Functions for releasing hints.
"""
from hunt.models import *
from datetime import datetime


def maybe_release_hints():
    """
    Release any requested hints that have been delayed for the appropriate
    length of time.
    """
    for hunt_info in HuntInfo.objects.all():
        if check_hint_release(hunt_info):
            # Log an event
            event = HuntEvent()
            event.time = datetime.utcnow()
            event.team = hunt_info.user.username
            event.type = HuntEvent.HINT_REL
            event.level = hunt_info.level
            event.save()

            release_hint(hunt_info)


def check_hint_release(hunt_info):
    """
    Check whether we've passed the threshold to release the next hint.
    """
    time_now = datetime.now()
    return (hunt_info.hint_requested and
            hunt_info.next_hint_release is not None and
            time_now > hunt_info.next_hint_release)


def release_hint(hunt_info):
    """
    Updates the HuntInfo object to take into account that a hint has been released.
    """
    hunt_info.hints_shown += 1
    hunt_info.hint_requested = False
    hunt_info.next_hint_release = None
    hunt_info.save()
