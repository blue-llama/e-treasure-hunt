from django.contrib import admin

from hunt.models import AppSetting, Hint, HuntEvent, HuntInfo, Level, ChatMessage

# Register your models here.
admin.site.register(AppSetting)
admin.site.register(Hint)
admin.site.register(HuntEvent)
admin.site.register(HuntInfo)
admin.site.register(Level)
admin.site.register(ChatMessage)
