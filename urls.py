'''
Module that maps incoming URL requests to functions which return responses
'''

from django.conf.urls import patterns, include, url
from django.contrib import admin

from timetracker import views
from timetracker.tracker.models import Tbluser
from timetracker.utils.datemaps import gen_process_list

admin.autodiscover()

YEAR = '(?P<year>\d{4})'
MONTH = '(?P<month>\d{1,2})'
DAY = '(?P<day>\d{1,2})'
PROCESS = '/?(?P<process>%s)?'

PROCESS = PROCESS % gen_process_list()

# todo: tracker app needs to be made into it's own
#       app and then the main views in here will
#       just point to that.
urlpatterns = patterns('',
    url(r'^$', views.index),

    url(r'^calendar/?$', views.user_view),
    url(r'^calendar/%s/?$' % YEAR, views.user_view),
    url(r'^calendar/%s/%s/?$' % (YEAR, MONTH), views.user_view),
    url(r'^calendar/%s/%s/%s/?$' % (YEAR, MONTH, DAY), views.user_view),

    url(r'^holiday_planning%s$' % PROCESS,
        views.view_with_holiday_list,
        {"template":"holidays.html", "admin_required": True}),
    url(r'^holiday_planning/%s/%s%s$' % (YEAR, MONTH, PROCESS),
        views.view_with_holiday_list,
        {"template":"holidays.html", "admin_required": True}),

    url(r'^team_planning/?$', views.view_with_holiday_list,
        {"template":"team_planning.html"}),
    url(r'^team_planning/%s/%s/?$' % (YEAR, MONTH),
        views.view_with_holiday_list,
        {"template":"team_planning.html"}),

    url(r'^yearview/?(?P<who>\d+)?$', views.yearview),
    url(r'^yearview/?(?P<who>\d+)/%s/?$' % YEAR, views.yearview),

    url(r'^overtime/?(?P<who>\d+)?$', views.overtime),
    url(r'^overtime/?(?P<who>\d+)/%s/?$' % YEAR, views.overtime),

    url(r'^admin_view/?$', views.view_with_employee_list,
        {"template":"admin_view.html"}),
    url(r'^ajax/?$', views.ajax),
    url(r'^login/?$', views.login),
    url(r'^logout/?$', views.logout),
    url(r'^user_edit/?$', views.view_with_employee_list,
        {"template":"useredit.html","get_all":True}),
    url(r'^edit_profile/?$', views.edit_profile),
    url(r'^explain/?$', views.explain),
    url(r'^forgot_my_password/?$', views.forgot_pass),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    (r'^reporting/', include('timetracker.reporting.urls')),
    (r'^ot/', include('timetracker.overtime.urls')),
)
