'''
Views which are mapped from the URL objects in urls.py
'''

import datetime

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from tracker.models import Tbluser, UserForm, TrackingEntry
from tracker.models import Tblauthorization as tblauth
from tracker.forms import EntryForm, AddForm, Login

from utils.calendar_utils import (gen_calendar, gen_holiday_list,
                                  ajax_add_entry, ajax_change_entry,
                                  ajax_delete_entry, ajax_error,
                                  get_user_data, delete_user, useredit,
                                  mass_holidays, profile_edit)

from timetracker.utils.datemaps import generate_select
from timetracker.utils.decorators import admin_check, loggedin


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
        user = Tbluser.objects.get(user_id__exact=request.POST['user_name'])
        
    # if the user doesn't match anything, notify
    except Tbluser.DoesNotExist:
        return HttpResponse("Username and Password don't match")

    if user.password == request.POST['password']:

        # if all goes well, send to the tracker
        request.session['user_id'] = user.id
        request.session['firstname'] = user.firstname

        if user.is_admin():
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

@loggedin
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

    user_id = request.session['user_id']
    calendar_table = gen_calendar(year, month, day,
                                  user=user_id)
    balance = Tbluser.objects.get(id=user_id).get_total_balance(ret='int')
    return render_to_response(
        'calendar.html',
        {
         'calendar': calendar_table,
         'changeform': EntryForm(),
         'addform': AddForm(),
         'welcome_name': request.session['firstname'],
         'balance': balance
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
        'useredit': useredit,
        'delete_user': delete_user,
        'mass_holidays': mass_holidays,
        'profileedit': profile_edit
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

    # retrieve and assign user object
    admin_id = Tbluser.objects.get(id=request.session.get("user_id", None))
    
    try:
        employees = tblauth.objects.get(admin=admin_id)
        employees_select = generate_select(
            [ (user.id, user.name()) for user in employees.users.all() ],
            id="user_select"
        )
    except tblauth.DoesNotExist:
        employees = []
        employees_select = "<select id=user_select></select>"

    return render_to_response(
        "admin_view.html",
        {
        "employees": employees,
        'welcome_name': request.session['firstname'],
        'employee_option_list': employees_select
        },
        RequestContext(request)
    )


@admin_check
def add_change_user(request):

    """
    Creates the view for changing/adding users
    """
    
    # retrieve and assign user object
    auth = Tbluser.objects.get(
        id=request.session.get("user_id", None)
    )

    # if the user is actually a TeamLeader, they can
    # view the team assigned to their manager
    if auth.user_type == "TEAML":
        auth = tblauth.objects.get(
            users=request.session.get("user_id", None
        )).admin

    # since we now will have a manage either way,
    # via the team leader or the actual manager,
    # we get all the users and generate a select
    # option box.
    try:
        employees = tblauth.objects.get(admin_id=auth)
        employees_select = generate_select(
            [ (user.id, user.name()) for user in employees.users.all() ],
            id="user_select"
        )
    except tblauth.DoesNotExist:
        employees = []
        employees_select = "<select id=user_select></select>"

    return render_to_response(
        "useredit.html",
        {
        "employees": employees,
        "user_form": UserForm(),
        'welcome_name': request.session['firstname'],
        'employee_option_list': employees_select
        },
        RequestContext(request)
    )


@admin_check
def holiday_planning(request,
                     year=datetime.datetime.today().year,
                     month=datetime.datetime.today().month):
    """
    Generates the full holiday table for all employees under a manager
    """

    # if the admin/tl tries to access the holiday page
    # before any users have been assigned to them, then
    # we just throw them back to the main page. This is
    # doubly ensuring that they can't access what would
    # otherwise be a completely borked page.
    try:
        user = Tbluser.objects.get(
            id=request.session.get('user_id')
        )
    except Tbluser.DoesNotExist:
        return HttpResponseRedirect("/admin_view/")

    # if the user is actually a TeamLeader, they can
    # view the team assigned to their manager
    if user.user_type == "TEAML":
        user = tblauth.objects.get(
            users=request.session.get("user_id", None
        )).admin

    # whichever user we're left with,
    # get the users assigned to them
    auth = tblauth.objects.get(admin=user)

    return render_to_response(
        "holidays.html",
        {
        "holiday_table": gen_holiday_list(auth,
                                          int(year),
                                          int(month)),
        'welcome_name': request.session['firstname']
        },
        RequestContext(request))

@loggedin
def edit_profile(request):

    """
    View for sending the user to the edit profile page
    """

    user = Tbluser.objects.get(id=request.session.get("user_id"))

    balance = user.get_total_balance(ret='int')
    return render_to_response("editprofile.html",
                              {'firstname': user.firstname,
                               'lastname': user.lastname,
                               'welcome_name': request.session['firstname'],
                               'balance': balance
                               },
                              RequestContext(request))

@loggedin
def explain(request):

    """
    Renders the Balance explanation page
    """

    user = Tbluser.objects.get(id=request.session.get("user_id"))
    shift = str(user.shiftlength.hour) + ': ' + str(user.shiftlength.minute)
    working_days = TrackingEntry.objects.filter(user=user.id).count()

    balance = user.get_total_balance(ret='int')
    return render_to_response("balance.html",
                              {'firstname': user.firstname,
                               'lastname': user.lastname,
                               'welcome_name': request.session['firstname'],
                               'balance': balance,
                               'shiftlength': shift,
                               'working_days': working_days
                               },
                              RequestContext(request))
