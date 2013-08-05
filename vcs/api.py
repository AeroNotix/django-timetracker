from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication

from timetracker.vcs.models import ActivityEntry

class ActivityEntryResource(ModelResource):
    class Meta:
        queryset = ActivityEntry.objects.all()
        resource_name = "activityentries"
        authentication = ApiKeyAuthentication()
