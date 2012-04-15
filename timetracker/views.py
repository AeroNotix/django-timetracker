'''
Views which are mapped from the URL objects in urls.py
'''

import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

import simplejson

from tracker.models import TrackingEntry #, Tbluser
from utils.calendar_utils import (gen_calendar, ajax_add_entry,
                                  ajax_change_entry, ajax_delete_entry,
                                  ajax_error)
from utils.database_errors import *
from tracker.forms import entry_form, add_form

def index(request):
    """
    Serve the root page, there's nothing there at the moment
    """
    return render_to_response('base.html',
                              {},
                              RequestContext(request))


def view_calendar(request,
             year=datetime.date.today().year,
             month=datetime.date.today().month,
             day=datetime.date.today().day,
             ):

    """
    Generates a calendar based on the URL it receives.
    site.com/calendar/2012/02/, also takes a day
    just in case you want to add a particular view for a day, for example.

    The generated HTML is pretty printed
    """

    calendar_table = gen_calendar(year, month, day,
                                  user='aaron.france@hp.com')


    return render_to_response(
        'calendar.html',
        {
         'calendar': calendar_table,
         'changeform': entry_form(),
         'addform' : add_form()
        },
        RequestContext(request)
        )


def process_change_request(request):

    """
    Processes a change into the database from the calendar page
    """
    pass


def ajax(request):

    """
    Ajax request handler, dispatches to specific ajax functions
    depending on what json gets sent.
    """

    # if the page is accessed via the browser (or other means)
    # we don't serve requests
    if not request.is_ajax():
        raise Http404

    # see which form we're dealing with
    form_type = request.POST.get('form_type', None)
    
    #if there isn't one, we'll send an error back
    if not form_type:
        return ajax_error("Missing Form")
        
    try:
        # this could be mutated with a @register_ajax
        # decorator or something
        ajax_funcs = {
            'add': ajax_add_entry,
            'change': ajax_change_entry,
            'delete': ajax_delete_entry
            }
        
        return ajax_funcs.get(form_type,
                              ajax_error("Form not found")
                              )(request)

    # if any errors are sent, let the page deal with it
    except Exception as e:
        return ajax_error(str(e))
