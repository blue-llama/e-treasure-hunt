from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.template import loader
from hunt.models import *
from hunt.levels import *
from hunt.hints import *
from hunt.hint_mgr import create_level, create_answer
from hunt.utilities import get_users_active_levels
from hunt.forms import AnswerFormSet, LevelForm
from . import hint_mgr
from django.contrib.auth.models import Permission
import os
import csv

from datetime import datetime

# Simple true-false function to determine whether the hunt is live.
def is_working_hours():
    return False
    # time = datetime.utcnow()

    # if (time.weekday() > 4):
    # return False

    # if (time.hour < 8):
    # return False
    # elif (time.hour > 16):
    # return False
    # elif ((time.hour == 16) and (time.minute >= 30)):
    # return False
    # elif ((time.hour == 11) and (time.minute >= 30)):
    # return False
    # elif ((time.hour == 12) and (time.minute < 30)):
    # return False

    # return True


# Send users to the hunt and admins to management.
@login_required
def go_home(request):
    if is_working_hours():
        return HttpResponse(loader.get_template("work-time.html").render({}, request))

    if request.user.is_staff:
        return redirect("/mgmt")
    else:
        return redirect("/home")


# Admin-only page to download hunt event logs.
@user_passes_test(lambda u: u.is_staff)
def get_hunt_events(request):

    meta = HuntEvent._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
    writer = csv.writer(response)

    writer.writerow(field_names)

    queryset = HuntEvent.objects.all()
    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response


# Hunt homepage.
@login_required
def home(request):
    if is_working_hours():
        return HttpResponse(loader.get_template("work-time.html").render({}, request))

    template = loader.get_template("welcome.html")

    hunt_info = request.user.huntinfo

    context = {
        "display_name": request.user.get_full_name(),
        "highest_level": get_users_active_levels(request.user)[0],
    }
    return HttpResponse(template.render(context, request))


# Level page.
@login_required
def level(request):
    if is_working_hours():
        return HttpResponse(loader.get_template("work-time.html").render({}, request))

    maybe_release_hints()
    return HttpResponse(maybe_load_level(request))


# Error page.
@login_required
def oops(request):
    if is_working_hours():
        return HttpResponse(loader.get_template("work-time.html").render({}, request))

    # Shouldn't be here. Show an error page.
    template = loader.get_template("oops.html")
    context = {"levels": get_users_active_levels(request.user)}

    # Return the rendered template.
    return HttpResponse(template.render(context, request))


# Map (or alt map).
@login_required
def map(request):
    if is_working_hours():
        return HttpResponse(loader.get_template("work-time.html").render({}, request))

    settings = AppSetting.objects.get(active=True)
    template = loader.get_template("map-base.html")
    if settings.use_alternative_map:
        template = loader.get_template("maphold.html")

    context = {
        "api_key": os.environ["GM_API_KEY"],
        "lvl": request.GET.get("lvl"),
    }
    return HttpResponse(template.render(context, request))


# Alt map.
@login_required
def alt_map(request):
    if is_working_hours():
        return HttpResponse(loader.get_template("work-time.html").render({}, request))

    template = loader.get_template("maphold.html")
    context = {
        "lvl": request.GET.get("lvl"),
    }
    return HttpResponse(template.render(context, request))


# Level list.
@login_required
def levels(request):
    if is_working_hours():
        return HttpResponse(loader.get_template("work-time.html").render({}, request))

    return HttpResponse(list_levels(request))


# Search request endpoint.
@login_required
def do_search(request):
    if is_working_hours():
        return HttpResponse(loader.get_template("work-time.html").render({}, request))

    return redirect(look_for_answers(request))


# Coordinate search page.
@login_required
def search(request):
    if is_working_hours():
        return HttpResponse(loader.get_template("work-time.html").render({}, request))

    lvl = request.GET.get("lvl")

    template = loader.get_template("search.html")
    context = {"lvl": lvl}

    return HttpResponse(template.render(context, request))


# Nothing here.
@login_required
def nothing(request):
    if is_working_hours():
        return HttpResponse(loader.get_template("work-time.html").render({}, request))

    template = loader.get_template("nothing.html")

    context = {"levels": get_users_active_levels(request.user)}
    return HttpResponse(template.render(context, request))


# Request a hint.
@login_required
def hint(request):
    if is_working_hours():
        return HttpResponse(loader.get_template("work-time.html").render({}, request))

    return redirect(request_hint(request))


# Management home.
@user_passes_test(lambda u: u.is_staff)
def mgmt(request):
    template = loader.get_template("mgmt.html")

    context = {
        "success": request.GET.get("success"),
    }
    return HttpResponse(template.render(context, request))


# Level uploader page.
@user_passes_test(lambda u: u.is_staff)
def hint_mgmt(request):
    template = loader.get_template("hint-mgmt.html")

    next = request.GET.get("next")
    if next == None:
        next = 1

    context = {"success": request.GET.get("success"), "next": next}
    return HttpResponse(template.render(context, request))


# Upload level endpoint.
@user_passes_test(lambda u: u.is_staff)
def add_new_level(request):
    return redirect(hint_mgr.upload_new_level(request))


# Admin force hint release.
@user_passes_test(lambda u: u.is_staff)
def do_release_hints(request):
    return redirect("/mgmt?success=" + str(release_hints()))


# Answer uploader page.
@user_passes_test(lambda u: u.is_staff)
def answer_mgmt(request):
    if request.method == "POST":
        levelform = LevelForm(request.POST, request.FILES)
        answerformset = AnswerFormSet(request.POST, request.FILES)
        if levelform.is_valid() and answerformset.is_valid():
            try:
                level = create_level(levelform.cleaned_data, request.FILES)
                for answerform in answerformset:
                    create_answer(level, answerform.cleaned_data)
            except:
                raise
    elif request.method == "GET":
        # GRT If we already have a level with some answers we should fill that in with them
        answerformset = AnswerFormSet()
        levelform = LevelForm()

    template = loader.get_template("answer-mgmt.html")
    context = {"level": levelform, "formset": answerformset}
    return HttpResponse(template.render(context, request))
