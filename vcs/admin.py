from django.contrib import admin

from timetracker.vcs import models

class ActivityAdmin(admin.ModelAdmin):
    pass

class ActivityEntryAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Activity, ActivityAdmin)
admin.site.register(models.ActivityEntry, ActivityEntryAdmin)
