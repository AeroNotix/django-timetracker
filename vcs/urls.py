'''
Module that maps incoming URL requests to functions which return responses
'''

from django.conf.urls import patterns, include, url
from timetracker.vcs import views

urlpatterns = patterns('',
                       (r'insert/?$', views.vcs),
                       (r'inserted/?$', views.vcs_add),
                       (r'entries', views.entries),
                       (r'update', views.update),
)
