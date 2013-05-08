from django.conf.urls import patterns, include, url

from timetracker.reporting import views
from timetracker.utils.datemaps import gen_team_list

YEAR = '(?P<year>\d{4})'
MONTH = '(?P<month>\d{1,2})'
TEAM = '(?P<team>%s)'

TEAM = TEAM % gen_team_list()

urlpatterns = patterns(
    '',
    url(r'^/?$', views.reporting),
    url(r'^all/(?P<who>\d+)/?$', views.download_all_holiday_data),
    url(r'^yearmonthhol/%s/%s/?$' % (YEAR, MONTH), views.yearmonthhol),
    url(r'^ot_by_month/%s/%s/?$' % (YEAR, MONTH), views.ot_by_month),
    url(r'^ot_for_hr/%s/%s/?$' % (YEAR, MONTH), views.ot_for_hr),
    url(r'^ot_by_year/%s/?$' % YEAR, views.ot_by_year),
    url(r'^hols_for_yearmonth/%s/?$' % YEAR, views.holidays_for_yearmonth),
)
