from django.shortcuts import render
from django.template import loader
from hunt.models import *
from datetime import *
from random import random

next_hint_time = None

def request_hint(request):
    # Request must be for a specific level - not allowed to request hints for old levels.
    lvl = request.GET.get('lvl')
    if (lvl == None):
        return "oops"
        
    # Check that this a request for the user's current level.
    lvl = int(lvl) 
    hunt_info = HuntInfo.objects.filter(user=request.user)[0]
    if (lvl != hunt_info.level):
        return "/oops"
        
    # Get the level that the hint has been requested for.
    level = UserLevel.objects.filter(level = lvl, user = request.user)[0]
    
    # Release hints now if they're due.
    maybe_release_hints()
    
    # Log an event to say there's been a hint request.
    event = HuntEvent()
    event.time = datetime.utcnow()
    event.type = HuntEvent.HINT_REQ
    event.team = request.user.username
    event.level = lvl
    event.save()
    
    # Set hint request flag on the user level, and save.
    level.hint_requested = True
    level.save()
    
    # Set hint request flag on the user, and save.
    hunt_info.hint_requested = True
    hunt_info.save()
    
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
    
def release_hints():    
    # First figure out when we should next do this.
    determine_next_hint()
        
    # Now get all the users and levels.
    levels = UserLevel.objects.all()
    users = HuntInfo.objects.all()
    
    # Reset all team hint request flags
    for user in users:
        if user.hint_requested:
            user.hint_requested = False
            user.save()
        
    # Release hints for levels where this has been requested, and reset the flag.
    for level in levels:
        if level.hint_requested:
        
            # Log an event to say we're doing this.
            event = HuntEvent()
            event.team = level.user.username
            event.time = datetime.utcnow()
            event.type = HuntEvent.HINT_REL
            event.level = level.level
            event.save()
            
            # Increment the number of hints and reset the flag.
            level.hints_shown = level.hints_shown + 1
            level.hint_requested = False
            level.save()
    
    # Update the last max level to reflect that we've done rubber-banding.
    # Get the current max level and save it off.
    settings = AppSetting.objects.get(active=True)
    settings.last_max_level = settings.max_level
    settings.max_level = HuntInfo.objects.order_by('-level')[0].level
    
    # Save the settings
    settings.save()
            
    return True