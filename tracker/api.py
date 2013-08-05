from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization

from timetracker.tracker.models import Tbluser
from timetracker.tracker.trackingentry import TrackingEntry
from timetracker.utils.datemaps import MARKET_CHOICES_LIST


class TbluserResource(ModelResource):
    class Meta:
        queryset = Tbluser.objects.all()
        resource_name = 'users'
        excludes = ["password"]
        authentication = ApiKeyAuthentication()
        authorization = Authorization()

resources = []
for market in MARKET_CHOICES_LIST:
    class Klass(ModelResource):
        class Meta:
            queryset = Tbluser.objects.filter(market=market)
            resource_name = 'user/%s' % market
            excludes = ["password"]
            authentication = ApiKeyAuthentication()
    resources.append(Klass)

class TrackingEntryResource(ModelResource):
    user = fields.ToOneField("timetracker.tracker.api.TbluserResource", "user")
    class Meta:
        queryset = TrackingEntry.objects.all()
        resource_name = 'trackingentries'
        authentication = ApiKeyAuthentication()
 
