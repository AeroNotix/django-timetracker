from django.conf.urls import patterns, include, url

from timetracker.reporting import views

YEAR = '(?P<year>\d{4})'
MONTH = '(?P<month>\d{1,2})'

urlpatterns = patterns(
    '',
    url(r'^/?$', views.reporting),
    url(r'^all/(?P<who>\d+)/?$', views.download_all_holiday_data),
    url(r'^yearmonthhol/%s/%s/?$' % (YEAR, MONTH), views.yearmonthhol),
    url(r'^ot_by_month/%s/%s/?$' % (YEAR, MONTH), views.ot_by_month),
    url(r'^ot_by_year/%s/?$' % YEAR, views.ot_by_year),
    url(r'^hols_for_yearmonth/%s/?$' % YEAR, views.holidays_for_yearmonth),
)
