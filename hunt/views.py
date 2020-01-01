from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.template import loader
from hunt.models import *
from hunt.levels import *
from hunt.hints import *
from . import hint_mgr
from django.contrib.auth.models import Permission
import os
import csv

from datetime import datetime

# Simple true-false function to determine whether the hunt is live.
def is_working_hours():
    return False
    #time = datetime.utcnow()
    
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
    if (is_working_hours()):
        return HttpResponse(loader.get_template('work-time.html').render({}, request))
        
    if (request.user.is_staff):
        return redirect('/mgmt')
    else:
        return redirect('/home')

# Admin-only page to download hunt event logs.        
@user_passes_test(lambda u: u.is_staff)
def get_hunt_events(request):
    
    meta = HuntEvent._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
    writer = csv.writer(response)

    writer.writerow(field_names)
    
    queryset = HuntEvent.objects.all()
    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response

# Hunt homepage.
@login_required
def home(request):
    if (is_working_hours()):
        return HttpResponse(loader.get_template('work-time.html').render({}, request))

    template = loader.get_template('welcome.html')
    
    hunt_info = request.user.huntinfo
    # GRT This doesn't exist anymore
    team_level = hunt_info.level
    
    # Hack - staff can see all levels.
    if (request.user.is_staff):
        team_level = Level.objects.order_by('-number')[0].number
    
    context = {
        'display_name': request.user.get_full_name(),
        'team_level': team_level,
        'hint_requested': hunt_info.hint_requested,
    }
    return HttpResponse(template.render(context, request))

# Level page.
@login_required   
def level(request):
    if (is_working_hours()):
        return HttpResponse(loader.get_template('work-time.html').render({}, request))
        
    maybe_release_hints()
    return HttpResponse(maybe_load_level(request))
    
# Error page.
@login_required   
def oops(request):
    if (is_working_hours()):
        return HttpResponse(loader.get_template('work-time.html').render({}, request))
        
    # Shouldn't be here. Show an error page.
    template = loader.get_template('oops.html')
    context = {
        'team_level': request.user.huntinfo.level
    }
           
    # Return the rendered template.
    return HttpResponse(template.render(context, request))

# Map (or alt map).
@login_required   
def map(request):
    if (is_working_hours()):
        return HttpResponse(loader.get_template('work-time.html').render({}, request))
    
    settings = AppSetting.objects.get(active=True);
    template = loader.get_template('map-base.html')
    if (settings.use_alternative_map):
        template = loader.get_template('maphold.html')
    
    context = { 
        'api_key': os.environ['GM_API_KEY'], 
        'lvl': request.GET.get('lvl'),
    }
    return HttpResponse(template.render(context, request))

# Alt map.
@login_required   
def alt_map(request):
    if (is_working_hours()):
        return HttpResponse(loader.get_template('work-time.html').render({}, request))
        
    template = loader.get_template('maphold.html')
    context = { 
        'lvl': request.GET.get('lvl'),
    }
    return HttpResponse(template.render(context, request))

# Level list.
@login_required   
def levels(request):
    if (is_working_hours()):
        return HttpResponse(loader.get_template('work-time.html').render({}, request))
        
    return HttpResponse(list_levels(request))

# Search request endpoint.  
@login_required   
def do_search(request):
    if (is_working_hours()):
        return HttpResponse(loader.get_template('work-time.html').render({}, request))

    return redirect(look_for_answers(request))

# Coordinate search page.
@login_required   
def search(request):
    if (is_working_hours()):
        return HttpResponse(loader.get_template('work-time.html').render({}, request))

    lvl = request.GET.get('lvl')

    template = loader.get_template('search.html')
    context = { 'lvl': lvl }
    
    return HttpResponse(template.render(context, request))

# Nothing here.
# GRT Ugh...
@login_required   
def nothing(request):
    if (is_working_hours()):
        return HttpResponse(loader.get_template('work-time.html').render({}, request))

    template = loader.get_template('nothing.html')
    
    lvl = request.GET.get('lvl')
    
    context = {
        'team_level': request.user.huntinfo.level,
        'search_level': lvl,
    }
    return HttpResponse(template.render(context, request))

# Request a hint.
@login_required   
def hint(request):
    if (is_working_hours()):
        return HttpResponse(loader.get_template('work-time.html').render({}, request))

    return redirect(request_hint(request))
  
# Management home.  
@user_passes_test(lambda u: u.is_staff)
def mgmt(request):
    template = loader.get_template('mgmt.html')

    context = {
        'success': request.GET.get('success'),
    }
    return HttpResponse(template.render(context, request))    

# Level uploader page.
@user_passes_test(lambda u: u.is_staff)
def hint_mgmt(request):
    template = loader.get_template('hint-mgmt.html')
    
    next = request.GET.get('next')
    if (next == None):
        next = 1
    
    context = {
        'success': request.GET.get('success'),
        'next': next
    }
    return HttpResponse(template.render(context, request))
    
# Upload level endpoint.
@user_passes_test(lambda u: u.is_staff)
def add_new_hint(request):
    return redirect(hint_mgr.upload_new_hint(request))

# Admin force hint release.
@user_passes_test(lambda u: u.is_staff)
def do_release_hints(request):
    return redirect('/mgmt?success=' + str(release_hints()))