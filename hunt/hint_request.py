"""
Functions for requesting hints.
"""
from hunt.models import *
from datetime import datetime, timedelta

# Time in minutes to wait for a hint to be dropped after a request.
LEADER_HINT_WAIT_TIME = 40
NON_LEADER_HINT_WAIT_TIME = 20


def request_hint(request):
    # Request must be for a specific level - not allowed to request hints for old levels.
    lvl = request.GET.get('lvl')
    if (lvl == None):
        return "oops"
        
    # Check that this a request for the user's current level.
    lvl = int(lvl) 
    hunt_info = HuntInfo.objects.filter(user=request.user)[0]
    if lvl != hunt_info.level:
        return "/oops"
        
    # Get the level that the hint has been requested for.
    level = UserLevel.objects.filter(level=lvl, user=request.user)[0]
    
    # If a hint request is already in progress, there's nothing to do here.
    # Just sent the user back to the level they're on.
    if level.hint_requested or hunt_info.hint_requested:
        return "/level/" + str(lvl)
    
    # Log an event to say there's been a hint request.
    event = HuntEvent()
    event.time = datetime.utcnow()
    event.type = HuntEvent.HINT_REQ
    event.team = request.user.username
    event.level = lvl
    event.save()
    
    process_hint_request(level)
    
    # Set hint request flag on the user, and save.
    hunt_info.hint_requested = True
    hunt_info.save()
    
    # Redirect back to the level in question.
    return "/level/" + str(lvl)


def get_furthest_active_level():
    """
    Finds the furthest level anyone has reached in the hunt by
    checking for the existence of UserLevel objects.
    """
    hunts = HuntInfo.objects.all()
    return max(hunt.level for hunt in hunts)


def in_the_lead(userlevel):
    """
    A user is in the lead if they are at the furthest active level
    anyone has reached and have received the most (or joint most)
    hints for that level.
    """
    if userlevel.level < get_furthest_active_level():
        return False

    users_on_this_level = UserLevel.objects.filter(level=userlevel.level)
    return userlevel.hints_shown == max(ul.hints_shown for ul in users_on_this_level)


def determine_hint_delay(userlevel):
    """
    Determine how long a user has to wait before seeing the next
    hint. Users who are in the lead have to wait longer than others.
    """
    if in_the_lead(userlevel):
        return LEADER_HINT_WAIT_TIME
    else:
        return NON_LEADER_HINT_WAIT_TIME


def process_hint_request(userlevel):
    """
    Sets fields on the userlevel to indicate that a hint request is in
    progress.
    """
    delay = determine_hint_delay(userlevel)
    userlevel.hint_requested = True
    userlevel.next_hint_release = datetime.now() + timedelta(minutes=delay)
    userlevel.save()
