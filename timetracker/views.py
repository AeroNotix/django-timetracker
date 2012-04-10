import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

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



