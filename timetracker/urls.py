'''
Module that maps incoming URL requests to functions which return responses
'''

from django.conf.urls import patterns, include, url
from django.contrib import admin

from timetracker import views

admin.autodiscover()

YEAR = '(?P<year>\d{4})'
MONTH = '(?P<month>\d{1,2})'
DAY = '(?P<day>\d{1,2})'

# todo: tracker app needs to be made into it's own
#       app and then the main views in here will
#       just point to that.
urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^calendar/?$', views.user_view),
    url(r'^calendar/%s/?$' % YEAR, views.user_view),
    url(r'^calendar/%s/%s/?$' % (YEAR, MONTH), views.user_view),
    url(r'^calendar/%s/%s/%s/?$' % (YEAR, MONTH, DAY), views.user_view),
    url(r'^holiday_planning/?$', views.holiday_planning),
    url(r'^holiday_planning/%s/%s/?$' % (YEAR, MONTH), views.holiday_planning),
    url(r'^admin_view/?$', views.admin_view),
    url(r'^ajax/?$', views.ajax),
    url(r'^login/?$', views.login),
    url(r'^logout/?$', views.logout),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^user_edit/?$', views.add_change_user),
    url(r'^edit_profile/?$', views.edit_profile),
    url(r'^explain/?$', views.explain),
)
