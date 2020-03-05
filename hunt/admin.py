from django.contrib import admin
from hunt.models import HuntInfo, Level, AppSetting, HuntEvent, UserLevel

# Register your models here.
admin.site.register(HuntInfo)
admin.site.register(Level)
admin.site.register(AppSetting)
admin.site.register(HuntEvent)
admin.site.register(UserLevel)