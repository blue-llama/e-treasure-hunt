import csv
import os

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from hunt.hint_mgr import upload_new_hint
from hunt.hint_release import maybe_release_hint
from hunt.hint_request import request_hint
from hunt.levels import list_levels, look_for_level, maybe_load_level
from hunt.models import AppSetting, HuntEvent, Level
from hunt.utils import not_in_working_hours


# Send users to the hunt and admins to management.
@login_required
@not_in_working_hours
def go_home(request: HttpRequest) -> HttpResponse:
    if request.user.is_staff:
        return redirect("/mgmt")

    return redirect("/home")


# Admin-only page to download hunt event logs.
@user_passes_test(lambda u: u.is_staff)
def get_hunt_events(request: HttpRequest) -> HttpResponse:

    meta = HuntEvent._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
    writer = csv.writer(response)

    writer.writerow(field_names)

    queryset = HuntEvent.objects.all()
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response


# Hunt homepage.
@login_required
@not_in_working_hours
def home(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("welcome.html")

    hunt_info = request.user.huntinfo
    team_level = hunt_info.level

    # Hack - staff can see all levels.
    if request.user.is_staff:
        team_level = Level.objects.order_by("-number")[0].number

    context = {"display_name": request.user.get_full_name(), "team_level": team_level}
    return HttpResponse(template.render(context, request))


# Level page.
@login_required
@not_in_working_hours
def level(request: HttpRequest) -> HttpResponse:
    maybe_release_hint(request.user)
    return HttpResponse(maybe_load_level(request))


# Error page.
@login_required
@not_in_working_hours
def oops(request: HttpRequest) -> HttpResponse:
    # Shouldn't be here. Show an error page.
    template = loader.get_template("oops.html")
    context = {"team_level": request.user.huntinfo.level}

    # Return the rendered template.
    return HttpResponse(template.render(context, request))


# Map (or alt map).
@login_required
@not_in_working_hours
def map(request: HttpRequest) -> HttpResponse:
    settings = AppSetting.objects.get(active=True)
    template_name = "maphold.html" if settings.use_alternative_map else "map-base.html"
    template = loader.get_template(template_name)

    context = {"api_key": os.environ["GM_API_KEY"], "lvl": request.GET.get("lvl")}
    return HttpResponse(template.render(context, request))


# Alt map.
@login_required
@not_in_working_hours
def alt_map(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("maphold.html")
    context = {"lvl": request.GET.get("lvl")}
    return HttpResponse(template.render(context, request))


# Level list.
@login_required
@not_in_working_hours
def levels(request: HttpRequest) -> HttpResponse:
    return HttpResponse(list_levels(request))


# Search request endpoint.
@login_required
@not_in_working_hours
def do_search(request: HttpRequest) -> HttpResponse:
    return redirect(look_for_level(request))


# Coordinate search page.
@login_required
@not_in_working_hours
def search(request: HttpRequest) -> HttpResponse:
    lvl = request.GET.get("lvl")

    template = loader.get_template("search.html")
    context = {"lvl": lvl}

    return HttpResponse(template.render(context, request))


# Nothing here.
@login_required
@not_in_working_hours
def nothing(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("nothing.html")

    team_level = request.user.huntinfo.level
    lvl = request.GET.get("lvl")
    search_level = None if lvl is None else int(lvl)

    context = {"team_level": team_level, "search_level": search_level}
    return HttpResponse(template.render(context, request))


# Request a hint.
@login_required
@not_in_working_hours
def hint(request: HttpRequest) -> HttpResponse:
    return redirect(request_hint(request))


# Management home.
@user_passes_test(lambda u: u.is_staff)
def mgmt(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("mgmt.html")

    context = {"success": request.GET.get("success")}
    return HttpResponse(template.render(context, request))


# Level uploader page.
@user_passes_test(lambda u: u.is_staff)
def hint_mgmt(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("hint-mgmt.html")

    next_level = request.GET.get("next")
    if next_level is None:
        next_level = "1"

    context = {"success": request.GET.get("success"), "next": next_level}
    return HttpResponse(template.render(context, request))


# Upload level endpoint.
@user_passes_test(lambda u: u.is_staff)
def add_new_hint(request: HttpRequest) -> HttpResponse:
    return redirect(upload_new_hint(request))
