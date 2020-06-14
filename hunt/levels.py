import sys
from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.http.request import HttpRequest
from django.template import loader
from geopy import distance
from storages.backends.dropbox import DropBoxStorage

import hunt.slack as slack
from hunt.models import HuntEvent, Level


def advance_level(user: User) -> None:
    hunt_info = user.huntinfo
    new_level = hunt_info.level + 1

    # Log an event to record this.
    event = HuntEvent()
    event.time = datetime.now(timezone.utc)
    event.type = HuntEvent.CLUE_ADV
    event.team = user.username
    event.level = new_level
    event.save()

    # Update the team's level, clear any hint request flags and save.
    hunt_info.level = new_level
    hunt_info.hints_shown = 1
    hunt_info.hint_requested = False
    hunt_info.next_hint_release = None
    hunt_info.save()

    # Cancel any pending slack announcements.
    if hunt_info.slack_channel:
        slack.cancel_pending_announcements(hunt_info.slack_channel)


def look_for_level(request: HttpRequest) -> str:
    # Get latitude and longitude - without these there can be no searching.
    latitude = request.GET.get("lat")
    longitude = request.GET.get("long")
    if (latitude is None) or (longitude is None):
        return "/search"

    # Every search must be for the solution to a specific level - by default, assume
    # this is the team's current level.
    user = request.user
    team_level = user.huntinfo.level
    lvl = request.GET.get("lvl")
    search_level = team_level if lvl is None else int(lvl)

    # Prevent searching for later levels.
    if search_level > team_level:
        return "/oops"

    # Get the distance between the search location and the level solution.
    level = Level.objects.get(number=search_level)
    level_coords = (level.latitude, level.longitude)
    search_coords = (latitude, longitude)
    dist = distance.distance(search_coords, level_coords).m

    # If the distance is small enough, accept the solution.
    if dist <= level.tolerance:
        if search_level == team_level:
            advance_level(user)

        # Redirect to the new level.
        return "/level/" + str(search_level + 1)

    # Redirect to a failure page.
    return "/nothing-here?lvl=" + str(search_level)


def maybe_load_level(request: HttpRequest, level_num: int) -> str:
    # Get the user details.
    user = request.user
    team = user.huntinfo

    # Find the last level.  Staff can see everything.
    max_level_num = Level.objects.order_by("-number")[0].number
    team_level_num = max_level_num if user.is_staff else team.level

    # Only load the level if it's one the team has access to.
    if level_num <= team_level_num:
        # Get the level objects for this level and the one before.
        previous_level = Level.objects.get(number=level_num - 1)
        current_level = Level.objects.get(number=level_num)

        # Figure out how many images to display.  Show all hints for solved levels.
        max_hints = sys.maxsize if level_num < team_level_num else team.hints_shown

        # Get the URLs for the images to show.
        fs = DropBoxStorage()
        hints = current_level.hint_set.filter(number__lt=max_hints).order_by("number")
        hint_urls = [fs.url(hint.filename) for hint in hints]

        # Is this the last level?
        is_last_level = current_level.number == max_level_num

        # Get the description from the previous level, and split it
        # into paragraphs for display.
        desc_paras = previous_level.description.splitlines()

        # By default a hint can be requested.
        allow_hint = True
        reason = ""

        # Don't allow a hint if one's already been requested by the team, or
        # if max hints are already shown.
        if team.hint_requested:
            allow_hint = False
            reason = "Your team has already requested a hint."
        elif team.hints_shown >= max_hints:
            allow_hint = False
            reason = "No more hints are available on this level."

        # Prepare the template and context.
        template = loader.get_template("level.html")
        context = {
            "team_level": team_level_num,
            "level_number": current_level.number,
            "level_name": previous_level.name.upper(),
            "hints": hint_urls,
            "desc_paras": desc_paras,
            "allow_hint": allow_hint,
            "reason": reason,
            "latitude": previous_level.latitude,
            "longitude": previous_level.longitude,
            "is_last": is_last_level,
        }
    else:
        # Shouldn't be here. Show an error page.
        template = loader.get_template("oops.html")
        context = {"team_level": team_level_num}

    # Return the rendered template.
    rendered: str = template.render(context, request)
    return rendered


def list_levels(request: HttpRequest) -> str:
    # Get the team's current level.
    team_level = request.user.huntinfo.level

    # Hack - staff can see all levels.
    if request.user.is_staff:
        team_level = Level.objects.order_by("-number")[0].number

    # Make a list of all the levels to display.
    levels = list(range(1, team_level + 1))

    # Give the level list as context to the template.
    template = loader.get_template("levels.html")
    context = {"team_level": team_level, "levels": levels}

    # Return the rendered template.
    rendered: str = template.render(context, request)
    return rendered
