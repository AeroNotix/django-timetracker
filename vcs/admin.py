from django.contrib import admin

from timetracker.vcs import models

class ActivityAdmin(admin.ModelAdmin):
    search_fields = ["group", "grouptype", "groupdetail", "details",
                     "costbucket"]

class ActivityEntryAdmin(admin.ModelAdmin):
    pass

class ActivityOffsetAdmin(admin.ModelAdmin):
    pass

class OffsetAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Activity, ActivityAdmin)
admin.site.register(models.ActivityEntry, ActivityEntryAdmin)
admin.site.register(models.ActivityOffset, ActivityOffsetAdmin)
admin.site.register(models.Offset, OffsetAdmin)
