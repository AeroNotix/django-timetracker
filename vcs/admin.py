import random
import datetime

from django.contrib import admin

from timetracker.vcs import models
from timetracker.tracker.models import Tbluser


def add_random_activity_entries(modeladmin, request, queryset):
    users = Tbluser.objects.all()
    if len(users) == 0:
        return
    activities = models.Activity.objects.all()
    if len(users) == 0:
        return
    activity_entries = []
    for _ in xrange(10000):
        user = random.choice(users)
        activity = random.choice(activities)
        activity_entries.append(
            models.ActivityEntry(
                creation_date=datetime.datetime.today(),
                user=user,
                activity=activity,
                amount=random.choice(xrange(50))
            )
        )
    models.ActivityEntry.objects.bulk_create(activity_entries)

class ActivityAdmin(admin.ModelAdmin):
    search_fields = ["group", "grouptype", "groupdetail", "details",
                     "costbucket"]

class ActivityEntryAdmin(admin.ModelAdmin):
    actions = [add_random_activity_entries]

class ActivityOffsetAdmin(admin.ModelAdmin):
    pass

class OffsetAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Activity, ActivityAdmin)
admin.site.register(models.ActivityEntry, ActivityEntryAdmin)
admin.site.register(models.ActivityOffset, ActivityOffsetAdmin)
admin.site.register(models.Offset, OffsetAdmin)
