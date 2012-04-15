from django.conf.urls import patterns, include, url
from django.contrib import admin

from timetracker import views

admin.autodiscover()

year = '(?P<year>\d{4})'
month = '(?P<month>\d{1,2})'
day = '(?P<day>\d{1,2})'

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^calendar$', views.view_calendar),
    url(r'^calendar/$', views.view_calendar),
    url(r'^calendar/%s/?$' % year, views.view_calendar),
    url(r'^calendar/%s/%s/?$' % (year, month), views.view_calendar),
    url(r'^calendar/%s/%s/%s/?$' % (year, month, day), views.view_calendar),
    url(r'^ajax/?$', views.ajax),
    url(r'^login/?$', views.login),
    url(r'^logout/?$', views.logout),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
