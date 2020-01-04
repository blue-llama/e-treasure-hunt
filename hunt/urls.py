"""treasure URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from . import views
from django.contrib.admin.views.decorators import staff_member_required

urlpatterns = [
    path("", views.go_home, name="go-home"),
    re_path("^level/[0-9]+$", views.level, name="level"),
    path("levels/", views.levels, name="levels"),
    path("search", views.search, name="search"),
    path("do-search", views.do_search, name="do-search"),
    path("nothing-here", views.nothing, name="nothing-here"),
    path("hint", views.hint, name="hint"),
    path("home", views.home, name="home"),
    path("map", views.map, name="map"),
    path("alt-map", views.alt_map, name="alt-map"),
    path("oops", views.oops, name="oops"),
    path("events", views.get_hunt_events, name="events"),
    path("mgmt", views.mgmt, name="mgmt"),
    path("hint-mgmt", views.hint_mgmt, name="hint-mgmt"),
    path("add-level", views.add_new_level, name="add-level"),
    path("answer-mgmt", views.answer_mgmt, name="answer-mgmt"),
    path("hint-release", views.do_release_hints, name="hint-release"),
    path("level-mgmt", views.level_mgmt, name="level-mgmt"),
    path("graph", views.graph, name="graph"),
    path("test", views.test, name="test"),
]  
