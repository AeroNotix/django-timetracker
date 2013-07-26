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
    d1 = datetime.date(year=datetime.datetime.today().year,
                       month=1,
                       day=1)
    d2 = datetime.date(year=datetime.datetime.today().year,
                       month=12,
                       day=31)
    diff = d2 - d1
    dates = [d1 + datetime.timedelta(days=i) for i in range(diff.days)]
    for _ in xrange(30000):
        user = random.choice(users)
        activity = random.choice(activities)
        activity_entries.append(
            models.ActivityEntry(
                creation_date=random.choice(dates),
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
