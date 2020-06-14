from django.contrib import admin

from hunt.models import AppSetting, HuntEvent, HuntInfo, Level

# Register your models here.
admin.site.register(HuntInfo)
admin.site.register(Level)
admin.site.register(AppSetting)
admin.site.register(HuntEvent)
