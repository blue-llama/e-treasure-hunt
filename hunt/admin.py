from django.contrib import admin
from hunt.models import (
    HuntInfo,
    Level,
    HintTime,
    AppSetting,
    HuntEvent,
    Answer,
    UserLevel,
    Location
)

# Register your models here.
admin.site.register(HuntInfo)
admin.site.register(Level)
admin.site.register(HintTime)
admin.site.register(AppSetting)
admin.site.register(HuntEvent)
admin.site.register(Answer)
admin.site.register(UserLevel)
admin.site.register(Location)
