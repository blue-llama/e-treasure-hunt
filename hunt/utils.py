import datetime
from functools import wraps
from typing import Any, Callable

import holidays
import pytz
from django.contrib.auth.models import User
from django.db.models import Max
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.template import loader

from hunt.models import AppSetting, Level


class AuthenticatedHttpRequest(HttpRequest):
    user: User


RequestHandler = Callable[..., HttpResponse]


def max_level() -> int:
    max_level: int = Level.objects.all().aggregate(Max("number"))["number__max"]
    return max_level


# Are we in (UK) working hours?
def is_working_hours() -> bool:
    london = pytz.timezone("Europe/London")
    now = datetime.datetime.now(tz=london)

    # Prevent access before the start time, if configured.
    start = None
    try:
        settings = AppSetting.objects.get(active=True)
        start = settings.start_time
    except AppSetting.DoesNotExist:
        pass

    if start is not None and now < start:
        return True

    # Allow access at the weekend.
    if now.weekday() > 4:
        return False

    # Allow access on bank holidays.
    if now.date() in holidays.CountryHoliday("UK"):
        return False

    # Prevent access 9:00 - 12:30, and 13:30 - 17:30.
    clock = now.time()
    if datetime.time(9, 0) < clock < datetime.time(12, 30):
        return True

    if datetime.time(13, 30) < clock < datetime.time(17, 30):
        return True

    # We don't work other times.
    return False


# Decorator that prevents most users from accessing the site during working hours.
def not_in_working_hours(f: RequestHandler) -> RequestHandler:
    @wraps(f)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if (not request.user.is_staff) and is_working_hours():
            template = loader.get_template("work-time.html").render({}, request)
            return HttpResponse(template)

        return f(request, *args, **kwargs)

    return wrapper
