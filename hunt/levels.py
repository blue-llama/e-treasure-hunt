from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import loader
from hunt.models import *
from hunt.utilities import (
    get_users_active_levels,
    get_user_level_for_level,
    get_max_level_number,
    get_all_level_numbers,
)
from geopy import distance
import ast
from datetime import datetime

from storages.backends.dropbox import DropBoxStorage


def advance_level(hunt, answer):
    """ Carry out all the necessary admin to advance a level. """
    update_active_levels(hunt, answer)
    log_level_advance(hunt, answer)


def log_level_advance(hunt, answer):
    """ Log an event that a level has been solved. """
    event = HuntEvent()
    event.time = datetime.utcnow()
    event.type = HuntEvent.CLUE_ADV
    event.team = hunt.user.username
    event.level = answer.leads_to_level.number
    event.save()


def get_latitude_longitude(request):
    """ 
    Gets the latitude and longitude of this guess.
    Note, the request is always a GET because the map uses javascripts window.location.href to redirect.
    """
    return request.GET.get("lat"), request.GET.get("long")


def valid_search(request):
    """ Determines if this is a valid search. """
    latitude, longitude = get_latitude_longitude(request)
    return (latitude != None) and (longitude != None)


def get_distance(search_coords, answer_coords):
    """ Get the distance between the guess and the answer in metres. """
    return distance.distance(search_coords, answer_coords).m


def is_correct_answer(latitude, longitude, location):
    """ Determine if a given co-ordinate satisfies an answer. """
    distance = get_distance(
        (latitude, longitude), (location.latitude, location.longitude)
    )
    if distance <= location.tolerance:
        return True

    return False


def create_new_user_level(hunt, level):
    user_level = UserLevel(hunt=hunt, level=level)
    user_level.save()


def update_active_levels(hunt, answer):
    """ Update the hunt info's list of active levels. """
    create_new_user_level(hunt, answer.leads_to_level)


def get_search_level(request):
    return request.GET.get("lvl")


def look_for_answers(request):
    """
    Look to see if this search matches any answers to levels this user is currently on
    """
    if not valid_search(request):
        return "/search"

    latitude, longitude = get_latitude_longitude(request)

    # Get all the levels the user is currently working on
    hunt = request.user.huntinfo
    active_level_objects = hunt.active_levels.all()

    # For each active level, check if this is an answer
    for user_level in active_level_objects:
        for answer in user_level.level.answers.all():
            if is_correct_answer(latitude, longitude, answer.location):
                advance_level(hunt, answer)
                return "/level/" + str(answer.leads_to_level.number)

    # No correct answer found, redirect to a failure page.
    return "/nothing-here"


def get_hints_to_show(level, user_level):
    """
    Gets the images to show for this level.
    """
    num_hints = min(5, user_level.hints_shown)

    # Get the clue image names as an array, and select the ones to show.
    hints = ast.literal_eval(level.clues)
    hints_temp = hints[0:num_hints]

    # Get actual hint URLs from DropBox.
    hints_to_show = []
    fs = DropBoxStorage()
    for hint in hints_temp:
        hints_to_show.append(fs.url(hint))
    return hints_to_show


def can_request_hint(user_level):
    """
    Can a hint be requested for this user level.
    A hint can't be requested if:
    - A hint has already been requested
    - We've displayed all the hints available
    """
    allow_hint = True
    reason = ""

    # Don't allow a hint if one's already been requested by the team, or
    # if max hints are already shown.
    if user_level.hint_requested:
        allow_hint = False
        reason = "Your team has already requested a hint."
    elif user_level.hints_shown >= 5:
        allow_hint = False
        reason = "No more hints are available on this level."

    return allow_hint, reason


def get_level_numbers(request):
    # If this user is staff, return all the levels
    if request.user.is_staff:
        level_numbers = get_all_level_numbers()
    else:
        level_numbers = get_users_active_levels(request.user.huntinfo)

    return level_numbers


def get_answer_for_last_level(level_num):
    """
    Get the answer for the last level, that is, an answer which leads to this level.
    
    There may be multiple levels that lead to this level, assume the first has all the necessary information.
    """
    return Answer.objects.filter(leads_to_level__number=level_num)[0]


def maybe_load_level(request):
    # Figure out which level is being requested - this is the
    # number at the end of the URL.
    level_num = int(request.path.rsplit("/", 1)[-1])
    active_level_numbers = get_level_numbers(request)

    # Only load the level if it's one the team has access (staff have access to all levels).
    if level_num in active_level_numbers:
        # Get the level objects for this level and the one before.
        answer_for_last_level = get_answer_for_last_level(level_num)
        current_level = Level.objects.get(number=level_num)

        # Figure out how many images to display. This is the base number for
        # the level plus any private hints the team might have access to.
        user_level = get_user_level_for_level(current_level, request.user.huntinfo)
        hints_to_show = get_hints_to_show(current_level, user_level)

        # Is this the last level?
        is_last_level = current_level.number == get_max_level_number()

        # Get the description from the previous level, and split it
        # into paragraphs for display.
        desc_paras = answer_for_last_level.description.splitlines()

        # By default a hint can be requested.
        allow_hint, reason = can_request_hint(user_level)

        # Prepare the template and context.
        template = loader.get_template("level.html")
        context = {
            "highest_level": all_active_levels[0],
            "current_level": current_level.number,
            "level_name": answer_for_last_level.name.upper(),
            "hints": hints_to_show,
            "desc_paras": desc_paras,
            "allow_hint": allow_hint,
            "reason": reason,
            "latitude": answer_for_last_level.latitude,
            "longitude": answer_for_last_level.longitude,
            "is_last": is_last_level,
        }
    else:
        # Shouldn't be here. Show an error page.
        template = loader.get_template("oops.html")
        context = {"levels": sorted(active_level_numbers, reverse=True)}

    # Return the rendered template.
    return template.render(context, request)


def list_levels(request):
    level_numbers = get_level_numbers(request)

    # Give the level list as context to the template.
    template = loader.get_template("levels.html")
    context = {"levels": level_numbers}

    # Return the rendered template.
    return template.render(context, request)
