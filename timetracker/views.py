'''
Views which are mapped from the URL objects in urls.py
'''

import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

import simplejson

from tracker.models import TrackingEntry #, Tbluser
from utils.calendar_utils import gen_calendar, ajax_add_entry
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
    Ajax request handler, eventually this will dispatch to the
    specific ajax functions depending on what json gets sent.
    """

    error = ''

    # if the page is accessed via the browser (or other means)
    # we don't serve requests
    if not request.is_ajax():
        raise Http404

    # object to dump form data into
    form = {
        'entry_date': None,
        'start_time': None,
        'end_time': None,
        'daytype': None,
    }

    # get our form data
    for key in form:
        form[key] = request.POST.get(key, None)

    # create our JSON object
    json_data = {
        "success": False,
        "error": "",
        "calendar": ""
        }

    if request.POST.get('form_type') == 'add':
        json_data.update(ajax_add_entry(form))
    if request.POST.get('form_type') == 'change':
        json_data.update({"error": "Not implemented"})

    return HttpResponse(simplejson.dumps(json_data),
                        mimetype="application/javascript")

