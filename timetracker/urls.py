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

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^calendar$', views.view_calendar),
    url(r'^calendar/$', views.view_calendar),
    url(r'^calendar/%s/?$' % YEAR, views.view_calendar),
    url(r'^calendar/%s/%s/?$' % (YEAR, MONTH), views.view_calendar),
    url(r'^calendar/%s/%s/%s/?$' % (YEAR, MONTH, DAY), views.view_calendar),
    url(r'^ajax/?$', views.ajax),
    url(r'^login/?$', views.login),
    url(r'^logout/?$', views.logout),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
