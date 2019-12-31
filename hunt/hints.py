from django.shortcuts import render
from django.template import loader
from hunt.models import *
from hunt.utilities import get_users_active_levels, get_user_level_for_level
from datetime import *
from random import random

next_hint_time = None

def request_hint(request):
    # Request must be for a specific level - not allowed to request hints for old levels.
    lvl = request.GET.get('lvl')
    if (lvl == None):
        return "/oops"
        
    # Check that this a request for a level the user has access to.
    lvl = int(lvl) 
    active_levels = get_users_active_levels(request.user.huntinfo)
    if (lvl not in active_levels):
        return "/oops"
        
    # Get the level that the hint has been requested for.
    level = Level.objects.get(number = lvl)
    
    # Release hints now if they're due.
    maybe_release_hints()
    
    # Log an event to say there's been a hint request.
    event = HuntEvent()
    event.time = datetime.utcnow()
    event.type = HuntEvent.HINT_REQ
    event.team = request.user.username
    event.level = lvl
    event.save()
    
    if (hunt_info.private_hint_allowed):
        # Special - just do a private hint.
        hunt_info.hint_requested = True
        hunt_info.private_hint_requested = True
        hunt_info.private_hint_allowed = False
        hunt_info.save()
    else:
        # Set hint request flags on the user and level, and save.
        hunt_info.hint_requested = True
        hunt_info.save()
        user_level = get_user_level_for_level(level, hunt_info)
        user_level.hint_requested = True
        user_level.save()
    
    # Redirect back to the level in question.
    return "/level/" + str(lvl)
    
def maybe_release_hints():
    global next_hint_time
    
    # If global var isn't set then get it from the DB.
    if (next_hint_time == None):
        next_hint_time = AppSetting.objects.get(active=True).next_hint

    # If the next hint time has passed, we should release hints now.
    time_now = datetime.utcnow()       
    if (next_hint_time < time_now):
        release_hints()
    

def determine_next_hint():
    global next_hint_time
    
    # Look for hint times in the future.
    time_now = datetime.utcnow().time()
    print(time_now)
    future_hints = HintTime.objects.filter(time__gt=time_now)
    
    if (len(future_hints) == 0):
        # Next hint is first hint time, tomorrow.
        next_hint = HintTime.objects.order_by('time')[0]
        hint_day = datetime.today() + timedelta(days=1)
    else:
        # Next hint is next hint time, today.
        next_hint = future_hints.order_by('time')[0]
        hint_day = datetime.today()
    
    # Replace the time with the one from the next hint record to create the hint datetime.
    hint_time = hint_day.replace(hour=next_hint.time.hour, minute=next_hint.time.minute, second=0, microsecond=0)
    
    # Add some random time - between 0 and 40 mins. Use 2 random numbers to weight it towards 20 mins. 
    add_num = random() + random()
    add_secs = add_num*1200
    hint_time = hint_time + timedelta(seconds=add_secs)

    # Save the next hint time in the global var, and to the DB in case of webserver restart.
    next_hint_time = hint_time
    setting = AppSetting.objects.get(active=True)
    setting.next_hint = hint_time
    setting.save()

def release_private_hints():
    """ Release all private hints. """
    # GRT For now do nothing because it's really hard for private hints when you've no idea what level they need a hint for.
    return

    users = HuntInfo.objects.all()
    # Spin through users first to handle private hints.
    for user in users:
        # Special - maybe redact a private hint if someone else is releasing it now.
        if (user.private_hints_shown > 0):
            usr_lvl = Level.objects.get(number=user.level)
            if (usr_lvl.hint_requested):
                user.private_hints_shown -= 1
                user.save()
    
        # Special - maybe release a private hint.
        if user.private_hint_requested:
            usr_lvl = Level.objects.get(number=user.level)
            if (usr_lvl.hint_requested):
                # This hint wouldn't be private - reinstate the private hint allowance for later.
                user.private_hint_allowed = True
            else:
                # Release a private hint.
                user.private_hints_shown = user.private_hints_shown + 1
            
            # Reset hint request flags and save.
            user.private_hint_requested = False
            user.hint_requested = False
            user.save()
        
        # Reset the hint request flag for users who have requested regular hints.
        elif user.hint_requested:
            user.hint_requested = False
            user.save()

def release_level_hints():
    # Get all the user levels
    user_levels = UserLevel.objects.all()

    # Release hints for levels where this has been requested, and reset the flag.
    for user_level in user_levels:
        if user_level.hint_requested:
            # Log an event to say we're doing this.
            event = HuntEvent()
            event.time = datetime.utcnow()
            event.type = HuntEvent.HINT_REL
            event.level = user_level.level.number
            event.save()
            
            # Increment the number of hints and reset the flag.
            user_level.hints_shown = user_level.hints_shown + 1
            user_level.hint_requested = False
            user_level.save()

def release_rubber_banding_hints():
    # Rubber banding - we release hints for all clues which the most advanced team has passed during the last hint period.
    settings = AppSetting.objects.get(active=True);
    if (settings.last_max_level != settings.max_level):
        for ii in range(settings.last_max_level, settings.max_level):
            rubber_band_lvl = Level.objects.get(number=ii)
            for user_level in rubber_band_lvl.user_levels:
                if (user_level.hints_shown < 2):
                    user_level.hints_shown = 2
                    user_level.save()

def get_furthest_active_level():
    max_level = 0
    hunts = HuntInfo.objects.all()
    for hunt in hunts:
        active_levels = get_users_active_levels(hunt)
        highest_level = active_levels.sort()[-1]
        if highest_level > max_level:
            max_level = highest_level
    return max_level

def update_rubber_banding():
    # Update the last max level to reflect that we've done rubber-banding.
    # Get the current max level and save it off.
    settings.last_max_level = settings.max_level
    settings.max_level = get_furthest_active_level()
    settings.save()

def release_hints():    
    # First figure out when we should next do this.
    determine_next_hint()
    release_private_hints()
    release_level_hints()  
    release_rubber_banding_hints()
    update_rubber_banding()
    return True