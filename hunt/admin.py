from django.contrib import admin

from hunt.models import AppSetting, Hint, HuntEvent, HuntInfo, Level

# Register your models here.
admin.site.register(AppSetting)
admin.site.register(Hint)
admin.site.register(HuntEvent)
admin.site.register(HuntInfo)
admin.site.register(Level)
