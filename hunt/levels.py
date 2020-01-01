from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import loader
from hunt.models import *
from hunt.utilities import get_users_active_levels, get_user_level_for_level
from geopy import distance
import ast
from datetime import datetime

from storages.backends.dropbox import DropBoxStorage

def advance_level(hunt, answer):
    """ Carry out all the necessary admin to advance a level. """
    update_active_levels(hunt, answer)
    log_level_advance(hunt, answer)
    clear_private_hints(hunt)

def log_level_advance(hunt, answer):
    """ Log an event that a level has been solved. """
    event = HuntEvent()
    event.time = datetime.utcnow()
    event.type = HuntEvent.CLUE_ADV
    event.team = hunt.user.username
    event.level = answer.next_level.number
    event.save()

def clear_private_hints(hunt):
    """ Clear any private hint stuff, it's been used. """
    hunt.private_hint_requested = False
    hunt.private_hints_shown = 0
    hunt.save()

def get_latitude_longitude(request):
    """ 
    Gets the latitude and longitude of this guess.
    Note, the request is always a GET because the map uses javascripts window.location.href to redirect.
    """
    return request.GET.get('lat'), request.GET.get('long')

def valid_search(request):
    """ Determines if this is a valid search. """
    latitude, longitude = get_latitude_longitude(request)
    return ((latitude != None) and (longitude != None))

def get_distance(search_coords, answer_coords):
    """ Get the distance between the guess and the answer in metres. """
    return distance.distance(search_coords, answer_coords).m

def is_correct_answer(latitude, longitude, answer):
    """ Determine if a given co-ordinate satisfies an answer. """
    distance = get_distance((latitude, longitude), (answer.latitude, answer.longitude))
    if (distance <= answer.tolerance):
        return True

    return False

def create_new_user_level(hunt, level):
    user_level = UserLevel(hunt=hunt, level=level)
    user_level.save()

def update_active_levels(hunt, answer):
    """ Update the hunt info's list of active levels. """
    create_new_user_level(hunt, answer.next_level)

def look_for_answers(request):
    """
    Look to see if this search matches any answers to levels this user is currently on
    """
    if not valid_search(request):
        return "/search"

    latitude, longitude = get_latitude_longitude(request)

    # Get all the levels the user is currently working on  
    hunt = request.user.huntinfo
    active_level_objects = hunt.active_levels

    # For each active level, check if this is an answer
    for user_level in active_level_objects:
        for answer in user_level.level.answers:
            if is_correct_answer(latitude, longitude, answer):
                advance_level(answer, hunt)
                return "/level/" + str(answer.next_level.number)

    # No correct answer found, redirect to a failure page.
    return "/nothing-here?lvl=" + str(search_level)

# GRT - This needs to be updated to determine if a level has been unlocked by the team
def maybe_load_level(request):
    # Figure out which level is being requested - this is the 
    # number at the end of the URL.
    level_num = int(request.path.rsplit('/', 1)[-1])

    # Get the user's hunt progress information, including active levels.
    active_level_numbers = get_users_active_levels(request.user.huntinfo)

    # Figure out the maximum level number.
    max_level_num = Level.objects.order_by('-number')[0].number
    
    # Only load the level if it's one the team has access to or we're staff.
    if level_num in active_level_numbers or request.user.is_staff:
        # Get the level objects for this level and the one before.
        last_level = Level.objects.get(number = level_num - 1)
        current_level = Level.objects.get(number = level_num)
        
        # Figure out how many images to display. This is the base number for
        # the level plus any private hints the team might have access to.
        user_level = get_user_level_for_level(current_level, request.user.huntinfo)
        num_hints = min(5, user_level.hints_shown + team.private_hints_shown)
        
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
        
        # GRT This isn't going to work with multiple branches
        # Get the description from the previous level, and split it 
        # into paragraphs for display.
        desc_paras = last_level.description.splitlines()
        
        # By default a hint can be requested.
        allow_hint = True
        reason = ""
        
        # Don't allow a hint if one's already been requested by the team, or 
        # if max hints are already shown.
        if (hunt.hint_requested):
            allow_hint = False
            reason = "Your team has already requested a hint."
        elif (user_level.hints_shown >= 5):
            allow_hint = False
            reason = "No more hints are available on this level."
        
        # GRT Some of this context stuff will need updating
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
    level_numbers = get_users_active_levels(request.user.huntinfo)
    
    # Hack - staff can see all levels.
    if (request.user.is_staff):
        level_numbers = Level.objects.order_by('-number')[0].number
    
    # Give the level list as context to the template.
    template = loader.get_template('levels.html')
    context = {
        'levels': level_numbers
    }
     
    # Return the rendered template.
    return template.render(context, request)

    
