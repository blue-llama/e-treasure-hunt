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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from hunt import views
from hunt.apiviews import HintViewSet, LevelViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("levels", LevelViewSet, basename="level")
router.register("hints", HintViewSet, basename="hint")

urlpatterns = [
    path("", views.go_home, name="go-home"),
    path("level/<int:level>", views.level, name="level"),
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
    path("level-mgmt", views.level_mgmt, name="level-mgmt"),
    path("add-level", views.add_new_level, name="new-level"),
    path("api/", include(router.urls)),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
