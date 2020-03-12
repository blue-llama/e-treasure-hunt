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
    for level in UserLevel.objects.all():
        if check_hint_release(level):
            # Log an event
            event = HuntEvent()
            event.time = datetime.utcnow()
            event.team = level.user.username
            event.type = HuntEvent.HINT_REL
            event.level = level.number
            event.save()

            release_hint(level)

            level.user.hint_requested = False
            level.user.save()


def check_hint_release(level):
    """
    Check whether we've passed the threshold to release the next hint.
    """
    time_now = datetime.now()
    return (level.hint_requested and
            level.next_hint_release is not None and
            time_now > level.next_hint_release)


def release_hint(level):
    """
    Updates the UserLevel object to take into account that a hint has been released.
    """
    level.hints_shown += 1
    level.hint_requested = False
    level.next_hint_release = None
    level.save()