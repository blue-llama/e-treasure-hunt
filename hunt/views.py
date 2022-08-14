from __future__ import annotations

import contextlib
import csv
import os
from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from hunt.hint_request import maybe_release_hint, prepare_next_hint, request_hint
from hunt.level_mgr import upload_new_level
from hunt.levels import list_levels, look_for_level, maybe_load_level
from hunt.models import AppSetting, HuntEvent
from hunt.utils import max_level, no_players_during_lockout

if TYPE_CHECKING:
    from django.http.request import HttpRequest

    from hunt.utils import AuthenticatedHttpRequest


# Send users to the hunt and admins to management.
@login_required
@no_players_during_lockout
def go_home(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.user.is_staff:
        return redirect("/mgmt")

    return redirect("/home")


# Admin-only page to download hunt event logs.
@user_passes_test(lambda u: u.is_staff)
def get_hunt_events(request: HttpRequest) -> HttpResponse:
    meta = HuntEvent._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename={meta}.csv"
    writer = csv.writer(response)

    writer.writerow(field_names)

    queryset = HuntEvent.objects.all()
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response


# Hunt homepage.
@login_required
@no_players_during_lockout
def home(request: AuthenticatedHttpRequest) -> HttpResponse:
    template = loader.get_template("welcome.html")

    # Staff can see all levels.
    user = request.user
    team_level = max_level() if user.is_staff else user.huntinfo.level

    context = {"display_name": user.get_username(), "team_level": team_level}
    return HttpResponse(template.render(context, request))


# Level page.
@login_required
@no_players_during_lockout
def level(request: AuthenticatedHttpRequest, level: int) -> HttpResponse:
    # Release a hint, if appropriate.
    user = request.user
    maybe_release_hint(user)

    # Prepare the next hint, if appropriate.
    hunt_info = user.huntinfo
    if hunt_info.next_hint_release is None:
        prepare_next_hint(hunt_info)

    # Show the level.
    return HttpResponse(maybe_load_level(request, level))


# Error page.
@login_required
@no_players_during_lockout
def oops(request: AuthenticatedHttpRequest) -> HttpResponse:
    # Shouldn't be here. Show an error page.
    template = loader.get_template("oops.html")
    context = {"team_level": request.user.huntinfo.level}

    # Return the rendered template.
    return HttpResponse(template.render(context, request))


# Map (or alt map).
@login_required
@no_players_during_lockout
def map(request: AuthenticatedHttpRequest) -> HttpResponse:
    # If we're configured to use the alt map, do so.
    settings = None
    with contextlib.suppress(AppSetting.DoesNotExist):
        settings = AppSetting.objects.get(active=True)

    use_alternative_map = False if settings is None else settings.use_alternative_map
    if use_alternative_map:
        return alt_map(request)

    # If we don't have a Google Maps API key, use the alt map.
    gm_api_key = os.environ.get("GM_API_KEY")
    if gm_api_key is None:
        return alt_map(request)

    # Use the Google map.
    template = loader.get_template("google-map.html")
    context = {"api_key": gm_api_key, "lvl": request.GET.get("lvl")}

    return HttpResponse(template.render(context, request))


# Alt map.
@login_required
@no_players_during_lockout
def alt_map(request: AuthenticatedHttpRequest) -> HttpResponse:
    template = loader.get_template("alternate-map.html")
    arcgis_api_key = os.environ.get("ARCGIS_API_KEY")
    context = {"api_key": arcgis_api_key, "lvl": request.GET.get("lvl")}
    return HttpResponse(template.render(context, request))


# Level list.
@login_required
@no_players_during_lockout
def levels(request: AuthenticatedHttpRequest) -> HttpResponse:
    return HttpResponse(list_levels(request))


# Search request endpoint.
@login_required
@no_players_during_lockout
def do_search(request: AuthenticatedHttpRequest) -> HttpResponse:
    return redirect(look_for_level(request))


# Coordinate search page.
@login_required
@no_players_during_lockout
def search(request: AuthenticatedHttpRequest) -> HttpResponse:
    lvl = request.GET.get("lvl")

    template = loader.get_template("search.html")
    context = {"lvl": lvl}

    return HttpResponse(template.render(context, request))


# Nothing here.
@login_required
@no_players_during_lockout
def nothing(request: AuthenticatedHttpRequest) -> HttpResponse:
    template = loader.get_template("nothing.html")

    team_level = request.user.huntinfo.level
    lvl = request.GET.get("lvl")
    search_level = None if lvl is None else int(lvl)

    context = {"team_level": team_level, "search_level": search_level}
    return HttpResponse(template.render(context, request))


# Request a hint.
@login_required
@no_players_during_lockout
def hint(request: AuthenticatedHttpRequest) -> HttpResponse:
    return redirect(request_hint(request))


# Management home.
@user_passes_test(lambda u: u.is_staff)
def mgmt(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("mgmt.html")

    context = {"success": request.GET.get("success")}
    return HttpResponse(template.render(context, request))


# Level uploader page.
@user_passes_test(lambda u: u.is_staff)
def level_mgmt(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("level-mgmt.html")
    next_level = request.GET.get("next", 1)

    context = {"success": request.GET.get("success"), "next": next_level}
    return HttpResponse(template.render(context, request))


# Upload level endpoint.
@user_passes_test(lambda u: u.is_staff)
def add_new_level(request: HttpRequest) -> HttpResponse:
    return redirect(upload_new_level(request))
