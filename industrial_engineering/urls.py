'''
Module that maps incoming URL requests to functions which return responses
'''

from django.conf.urls import patterns, include, url
from timetracker.industrial_engineering import views

urlpatterns = patterns('',
                       (r'cb/?$', views.costbuckets),
)
