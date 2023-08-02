from __future__ import annotations

from typing import TYPE_CHECKING

from django.template import loader
from django.utils import timezone
from geopy import Point, distance

from hunt.constants import HINTS_PER_LEVEL
from hunt.models import ChatMessage, HuntEvent, Level
from hunt.utils import max_level

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from hunt.utils import AuthenticatedHttpRequest


def advance_level(user: User) -> None:
    hunt_info = user.huntinfo
    new_level = hunt_info.level + 1

    # Log an event to record this.
    event = HuntEvent()
    event.time = timezone.now()
    event.type = HuntEvent.CLUE_ADV
    event.user = user
    event.level = new_level
    event.save()

    # Update the team's level, clear any hint request flags and save.
    hunt_info.level = new_level
    hunt_info.hints_shown = 1
    hunt_info.hint_requested = False
    hunt_info.next_hint_release = None
    hunt_info.save()


def look_for_level(request: AuthenticatedHttpRequest) -> str:
    # Get latitude and longitude - without these there can be no searching.
    latitude = request.GET.get("lat")
    longitude = request.GET.get("long")
    if latitude is None or longitude is None:
        return "/search"

    # Every search must be for a specific level - by default, assume this is the team's
    # current level.
    user = request.user
    team_level = max_level() if user.is_staff else user.huntinfo.level
    lvl = request.GET.get("lvl")
    search_level = team_level if lvl is None else int(lvl)

    # Prevent searching for later levels.
    if search_level > team_level:
        return "/oops"

    # Make sure we're searching in a valid place.
    try:
        search_point = Point(latitude, longitude)
    except ValueError:
        return "/oops"

    # Get the distance between the search location and the level solution.
    level = Level.objects.get(number=search_level)
    level_point = Point(level.latitude, level.longitude)
    dist = distance.distance(search_point, level_point).m

    # If the distance is small enough, accept the solution.
    if dist <= level.tolerance:
        if search_level == team_level:
            advance_level(user)

        # Redirect to the new level.
        return f"/level/{search_level + 1}"

    # Redirect to a failure page.
    return f"/nothing-here?lvl={search_level}"


def maybe_load_level(request: AuthenticatedHttpRequest, level_num: int) -> str:
    # Get the user details.
    user = request.user
    team = user.huntinfo

    # Find the last level.  Staff can see everything.
    max_level_num = max_level()
    team_level = max_level_num if user.is_staff else team.level

    # Only load the level if it's one the team has access to.
    if 0 < level_num <= team_level:
        # Get this level and the one before.
        current_level = Level.objects.get(number=level_num)
        previous_level = Level.objects.get(number=level_num - 1)

        # Decide how many images to display.  Show all hints for solved levels.
        num_hints = HINTS_PER_LEVEL if level_num < team_level else team.hints_shown

        # Get the URLs for the images to show.
        hints = current_level.hints.filter(number__lt=num_hints).order_by("number")
        hint_urls = [hint.image.url for hint in hints]

        # Don't allow a hint if one has already been requested by the team, or if max
        # hints are already shown.
        if team.hint_requested:
            allow_hint = False
            reason = "Your team has already requested a hint."
        elif team.hints_shown >= HINTS_PER_LEVEL:
            allow_hint = False
            reason = "No more hints are available on this level."
        else:
            allow_hint = True
            reason = ""

        is_last_level = current_level.number == max_level_num
        desc_paras = previous_level.description.splitlines()

        template = loader.get_template("level.html")
        chatroom_name = request.user.username + "_" + str(current_level.number)
        context = {
            "team_level": team_level,
            "level_number": current_level.number,
            "level_name": previous_level.name.upper(),
            "hints": hint_urls,
            "desc_paras": desc_paras,
            "allow_hint": allow_hint,
            "reason": reason,
            "latitude": previous_level.latitude,
            "longitude": previous_level.longitude,
            "is_last": is_last_level,
            "chatroom": chatroom_name,
            "messages": ChatMessage.objects.filter(
                room=chatroom_name, team=request.user
            ),
        }
    else:
        # Shouldn't be here. Show an error page.
        template = loader.get_template("oops.html")
        context = {"team_level": team_level}

    rendered: str = template.render(context, request)
    return rendered


def list_levels(request: AuthenticatedHttpRequest) -> str:
    # Get the team's current level.  Staff can see all levels.
    user = request.user
    team_level = max_level() if user.is_staff else user.huntinfo.level

    def truncate(name: str) -> str:
        if len(name) > 20:
            return name[:20] + "..."
        return name

    done_levels = Level.objects.filter(number__gt=0, number__lt=team_level).order_by(
        "number"
    )
    levels = [
        {"number": level.number, "name": truncate(level.name)} for level in done_levels
    ]
    levels.append({"number": team_level, "name": "Latest level"})

    template = loader.get_template("levels.html")
    context = {"team_level": team_level, "levels": levels}

    rendered: str = template.render(context, request)
    return rendered
