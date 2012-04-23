'''
Views which are mapped from the URL objects in urls.py
'''

import datetime

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from tracker.models import Tbluser, UserForm
from tracker.models import Tblauthorization as tblauth
from tracker.forms import EntryForm, AddForm, Login
from utils.calendar_utils import (gen_calendar, ajax_add_entry,
                                  ajax_change_entry, ajax_delete_entry,
                                  ajax_error, get_user_data, admin_check,
                                  delete_user, add_user)

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

    Dispatches to admin/user depending on usertype
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

    # if the user doesn't match anything, notify
    except Tbluser.DoesNotExist:
        return HttpResponse("Username and Password don't match")

    if usr.password == request.POST['password']:

        # if all goes well, send to the tracker
        request.session['user_id'] = usr.id

        if usr.user_type == "ADMIN":
            return HttpResponseRedirect("/admin_view/")
        else:
            return HttpResponseRedirect("/calendar/")
    else:
        return HttpResponse("Login failed!")


def logout(request):

    """
    Simple logout function
    """

    try:
        del request.session['user_id']
    except KeyError:
        pass

    return HttpResponseRedirect("/")

def user_view(request,
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

    # this could be mutated with a @register_ajax
    # decorator or something
    ajax_funcs = {
        'add': ajax_add_entry,
        'change': ajax_change_entry,
        'delete': ajax_delete_entry,
        'admin_get': gen_calendar,
        'get_user_data': get_user_data,
        'add_user': add_user,
        'delete_user': delete_user
        }
    return ajax_funcs.get(form_type,
                          ajax_error("Form not found")
                          )(request)

@admin_check
def admin_view(request):

    """
    The user logged in is an admin, we show them a
    view based on their team
    """

    admin_id = request.session.get("user_id", None)

    try:
        employees = tblauth.objects.get(admin=admin_id)
    except tblauth.DoesNotExist:
        return HttpResponseRedirect("/calendar/")

    return render_to_response("admin_view.html",
                              {"employees": employees},
                               RequestContext(request))
@admin_check
def add_change_user(request):

    """
    Creates the view for changing/adding users
    """

    admin_id = request.session.get('user_id', None)

    try:
        employees = tblauth.objects.get(admin_id=admin_id)
    except tblauth.DoesNotExist:
        pass

    form = UserForm()
    
    return render_to_response(
        "useredit.html",
        {
        "employees": employees,
        "user_form": form
        },
        RequestContext(request)
    )

@admin_check
def holiday_planning(request):

    
    return HttpResponse("SUP")
