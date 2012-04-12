import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.template import RequestContext

import simplejson

from tracker.models import TrackingEntry, Tbluser
from utils.calendar_utils import gen_calendar
from tracker.forms import entry_form, add_form

def index(request):
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

    if not request.is_ajax():
        raise Http404

    form = {
        'entry_date': None,
        'start_time': None,
        'end_time': None,
        'daytype': None,
    }

    for key in form:
        form[key] = request.POST.get(key, None)

    # need to use sessions
    form['user_id'] = 1
    form['breaks'] = "00:15:00"

    # lol
    entry = TrackingEntry(**form)
    entry.save()

    return HttpResponse(e)
