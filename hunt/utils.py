from __future__ import annotations

import contextlib
import datetime
import zoneinfo
from functools import wraps
from typing import TYPE_CHECKING, Concatenate, ParamSpec, TypeAlias

import holidays
from django.db.models import Max
from django.http.response import HttpResponse
from django.template import loader

from hunt.models import AppSetting, Level

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.contrib.auth.models import User
    from django.http.request import HttpRequest

    class AuthenticatedHttpRequest(HttpRequest):
        user: User

    P = ParamSpec("P")
    AuthenticatedRequestHandler: TypeAlias = Callable[
        Concatenate[AuthenticatedHttpRequest, P], HttpResponse
    ]


def max_level() -> int:
    max_level: int = Level.objects.all().aggregate(Max("number"))["number__max"]
    return max_level


# Should players be locked out?  True before the hunt starts, and during UK working
# hours.
def players_are_locked_out() -> bool:
    london = zoneinfo.ZoneInfo("Europe/London")
    now = datetime.datetime.now(tz=london)

    # Prevent access before the start time, if configured.
    start = None
    with contextlib.suppress(AppSetting.DoesNotExist):
        settings = AppSetting.objects.get(active=True)
        start = settings.start_time

    if start is not None and now < start:
        return True

    # Allow access at the weekend.
    if now.weekday() > 4:
        return False

    # Allow access on bank holidays.
    if now.date() in holidays.country_holidays("UK"):
        return False

    # Prevent access 9:00 - 12:30, and 13:30 - 17:30.
    clock = now.time()
    if datetime.time(9, 0) < clock < datetime.time(12, 30):
        return True

    if datetime.time(13, 30) < clock < datetime.time(17, 30):
        return True

    # Allow access.
    return False


# Decorator that prevents players from accessing the site when they should be locked
# out.
def no_players_during_lockout(
    f: AuthenticatedRequestHandler[P],
) -> AuthenticatedRequestHandler[P]:
    @wraps(f)
    def wrapper(
        request: AuthenticatedHttpRequest, /, *args: P.args, **kwargs: P.kwargs
    ) -> HttpResponse:
        if not request.user.is_staff and players_are_locked_out():
            template = loader.get_template("work-time.html").render({}, request)
            return HttpResponse(template)

        return f(request, *args, **kwargs)

    return wrapper
