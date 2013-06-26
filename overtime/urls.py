'''
Module that maps incoming URL requests to functions which return responses
'''

from django.conf.urls import patterns, include, url
from django.contrib import admin
from timetracker.overtime import views

urlpatterns = patterns('',
                       (r'accept_edit/(?P<entry>\d+)/?$', views.accept_edit),
                       (r'accepted/?$', views.accepted),
                       (r'delete/(?P<entry>\d+)/?$', views.delete),
)

