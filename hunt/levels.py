from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import loader
from hunt.models import *
from geopy import distance
import ast
from datetime import datetime

from storages.backends.dropbox import DropBoxStorage

def advance_level(user, level):
    hunt_info = HuntInfo.objects.filter(user=user)[0]
    
    # User may only advance by one level at a time
    if (level == hunt_info.level + 1):

        # Log an event to record this.
        event = HuntEvent()
        event.time = datetime.utcnow()
        event.type = HuntEvent.CLUE_ADV
        event.team = user.username
        event.level = level
        event.save()

        # Update the team's level, clear any hint request flags and save.
        hunt_info.level = level
        hunt_info.hint_requested = False
        hunt_info.private_hint_requested = False
        hunt_info.private_hints_shown = 0
        hunt_info.save()
    
def look_for_level(request):

    # Get latitude and longitude - without these there can be no searching.
    lat = request.GET.get('lat')
    long = request.GET.get('long')
    if ((lat == None) or (long == None)):
        return "/search"
        
    # Every search must be for the solution to a specific level - by default, 
    # assume this is the team's current level.
    search_level = int(request.user.huntinfo.level)
    old_search = False
    
    # See if there's a particular level specified in the request.
    lvl = request.GET.get('lvl')
    if (lvl != None):
        if (int(lvl) < search_level):
            # The request specified a previous level - search for that,
            # but don't advance the team's level if the search matches.        
            old_search = True
            search_level = int(lvl)
     
        # If the search is for a level above the one the team's on, redirect them.
        elif (int(lvl) > search_level):
            return "/oops"
    
    # Get the level object corresponding to the search.
    level = Level.objects.filter(number = search_level)[0]
    
    # Get the distance between the search location and the level solution
    level_coords = (level.latitude, level.longitude)
    search_coords = (lat, long)
    
    # TODO: This doesn't work well around the antipode of the solution.
    # Consider simply catching the resulting exception and rejecting the 
    # guess - it could hardly be further from the right answer!
    dist = distance.vincenty(search_coords, level_coords).m
    
    # If the distance is small enough, accept the solution.
    if (dist <= level.tolerance):
        # If this wasn't a search for a previous level, advance.
        if (not old_search):
            advance_level(request.user, level.number + 1)
            
        # Redirect to the new level.
        return "/level/" + str(search_level + 1)
    else:
        # Redirect to a failure page.
        return "/nothing-here?lvl=" + str(search_level)

def maybe_load_level(request):
    # Figure out which level is being requested - this is the 
    # number at the end of the URL.
    level_num = int(request.path.rsplit('/', 1)[-1])
    
    # Get the user's hunt progress information, including current level.
    team = request.user.huntinfo
    team_level = team.level
    
    # Figure out the maximum level number.
    max_level_num = Level.objects.order_by('-number')[0].number
    
    # Hack - admins can see all levels.
    if (request.user.is_staff):
        team_level = max_level_num
    
    # Only load the level if it's one the team has access to.
    if level_num <= team_level:
        # Get the level objects for this level and the one before.
        last_level = Level.objects.filter(number = level_num - 1)[0]
        current_level = Level.objects.filter(number = level_num)[0]
        
        # Figure out how many images to display. This is the base number for
        # the level plus any private hints the team might have access to.
        num_hints = min(5, current_level.hints_shown + team.private_hints_shown)
        
        # Get the clue image names as an array, and select the ones to show.
        hints = ast.literal_eval(current_level.clues)        
        hints_temp = hints[0:num_hints]
        
        # Get actual hint URLs from DropBox.
        hints_to_show = []
        fs = DropBoxStorage()
        for hint in hints_temp:
            hints_to_show.append(fs.url(hint))
            
        # Is this the last level?
        is_last_level = (current_level.number == max_level_num)
        
        # Get the description from the previous level, and split it 
        # into paragraphs for display.
        desc_paras = last_level.description.splitlines()
        
        # By default a hint can be requested.
        allow_hint = True
        reason = ""
        
        # Don't allow a hint if one's already been requested by the team, or 
        # if max hints are already shown.
        if (team.hint_requested):
            allow_hint = False
            reason = "Your team has already requested a hint."
        elif (current_level.hints_shown >= 5):
            allow_hint = False
            reason = "No more hints are available on this level."
        
        # Prepare the template and context.
        template = loader.get_template('level.html')
        context = {
            'team_level': team_level,
            'level_number': current_level.number,
            'level_name': last_level.name.upper(),
            'hints': hints_to_show,
            'desc_paras': desc_paras,
            'allow_hint': allow_hint,
            'reason': reason,
            'latitude': last_level.latitude,
            'longitude': last_level.longitude,
            'is_last': is_last_level,
        }
    else:
        # Shouldn't be here. Show an error page.
        template = loader.get_template('oops.html')
        context = {
            'team_level': team_level
        }
        
    # Return the rendered template.
    return template.render(context, request)   
    
def list_levels(request):
    # Get the team's current level.
    team_level = request.user.huntinfo.level
    
    # Hack - staff can see all levels.
    if (request.user.is_staff):
        team_level = Level.objects.order_by('-number')[0].number
    
    # Make a list of all the levels to display.
    levels = []
    for level in range(team_level):
        levels.append(level + 1)
        
    # Give the level list as context to the template.
    template = loader.get_template('levels.html')
    context = {
        'team_level': team_level,
        'levels': levels
    }
     
    # Return the rendered template.
    return template.render(context, request)

    
