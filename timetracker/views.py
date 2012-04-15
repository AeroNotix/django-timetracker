'''
Views which are mapped from the URL objects in urls.py
'''

import datetime

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

import simplejson

from tracker.models import TrackingEntry, Tbluser
from utils.calendar_utils import (gen_calendar, ajax_add_entry,
                                  ajax_change_entry, ajax_delete_entry,
                                  ajax_error)
from tracker.forms import EntryForm, AddForm, Login

def index(request):
    """
    Serve the root page, there's nothing there at the moment
    """
    return render_to_response('index.html',
                              {'login': Login()},
                              RequestContext(request))

def login(request):

    """
    Basic login function.

    Will upgrade to show admin view if the user is an
    admin, for now will always show the user view.
    """

    # if this somehow gets requested via Ajax, then
    # send back a 404. 
    if request.is_ajax():
        raise Http404

    # if the csrf token is missing, that's a 404
    if not request.POST.get('csrfmiddlewaretoken', None):
        raise Http404
    
    try:
        # pull out the user from the POST and
        # match it against our db
        usr = Tbluser.objects.get(user_id__exact=request.POST['user_name'])
        if usr.password == request.POST['password']:

            # if all goes well, send to the tracker
            request.session['user_id'] = usr.id            
            return HttpResponseRedirect("/calendar/")
        else:
            return HttpResponse("Login failed!")
    # if the user doesn't match anything, notify
    except Tbluser.DoesNotExist:
        return HttpResponse("Username and Password don't match")

def logout(request):

    """
    Simple logout function
    """

    try:
        del request.session['user_id']
    except KeyError:
        pass

    return HttpResponseRedirect("/")

def view_calendar(request,
             year=datetime.date.today().year,
             month=datetime.date.today().month,
             day=datetime.date.today().day,
             ):

    """
    Generates a calendar based on the URL it receives.
    site.com/calendar/2012/02/, also takes a day
    just in case you want to add a particular view for a day,
    for example.
    
    The generated HTML is pretty printed
    """

    if not request.session.get('user_id', None):
        raise Http404

    
    calendar_table = gen_calendar(year, month, day,
                                  user=request.session['user_id'])

    return render_to_response(
        'calendar.html',
        {
         'calendar': calendar_table,
         'changeform': EntryForm(),
         'addform' : AddForm()
        },
        RequestContext(request)
        )

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
