'''Views which are mapped from the URL objects in urls.py

    .. moduleauthor:: Aaron France <aaron.france@hp.com>

    :platform: All
    :synopsis: Module which contains view functions that are mapped from urls
'''

import datetime

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse


from timetracker.tracker.models import Tbluser, UserForm, TrackingEntry
from timetracker.tracker.models import Tblauthorization as tblauth
from timetracker.tracker.forms import EntryForm, AddForm, Login

from timetracker.utils.calendar_utils import (gen_calendar, gen_holiday_list,
                                              ajax_add_entry,
                                              ajax_change_entry,
                                              ajax_delete_entry, ajax_error,
                                              get_user_data, delete_user,
                                              useredit, mass_holidays,
                                              profile_edit, gen_datetime_cal,
                                              get_comments, add_comment,
                                              remove_comment,
                                              get_tracking_entry_data,
                                              password_reminder)

from timetracker.utils.datemaps import (generate_select,
                                        generate_employee_box,
                                        generate_year_box)

from timetracker.utils.decorators import admin_check, loggedin
from timetracker.loggers import suspicious_log, email_log, error_log, debug_log


def user_context_manager(request):
    '''Context manager which always puts certain variables into the
    template context. This is because all pages require certain
    pieces of data so it's easier to push this work down to middleware
    '''
    try:
        user = Tbluser.objects.get(id=request.session.get("user_id"))
    except Tbluser.DoesNotExist:
        return {}
    return {
        "user": user,
        "logged_in_user": user,
        "welcome_name": user.firstname,
        "is_admin": user.super_or_admin(),
        "is_team_leader": user.is_tl(),
        "can_view_jobcodes": user.can_view_jobcodes(),
        "is_super": user.is_super(),
        "balance": user.get_normalized_balance(),
        "doculink": settings.DOCUMENTATION_BASE_URL,
        "approval_notifications": user.approval_notifications()
        }

def index(request):

    """This function serves the base login page. This view detects if the
    user is logged in. If so, redirects, else, serves them the login
    page.

    This function shouldn't be directly called, it's invocation is automatic

    :param request: Automatically passed. Contains a map of the httprequest
    :return: A HttpResponse object which is then passed to the browser

    """

    try:
        user = Tbluser.objects.get(id=request.session.get("user_id"))
    except Tbluser.DoesNotExist:
        return render_to_response('index.html',
                                  {'login': Login()},
                                  RequestContext(request))

    if request.session.get("user_id"):
        user = Tbluser.objects.get(id=request.session.get("user_id"))
    if user.sup_tl_or_admin():
        return HttpResponseRedirect("/overtime/")
    if user.is_indeng():
        return HttpResponseRedirect(reverse("timetracker.industrial_engineering.views.costbuckets"))
    return HttpResponseRedirect("/calendar/")

def login(request):

    """This function logs the user in, directly adding the session id to a
    database entry. This function is invoked from the url mapped in
    urls.py.  The url is POSTed to, and should contain two fields, the
    use_name and the pass word field. This is then pulled from the
    database and matched against, what the user supplied. If they
    match, the user is then checked to see what *kind* of user their
    are, if they are ADMIN or TEAML they will be sent to the
    administrator view. Else they will be sent to the user page.

    This function shouldn't be directly called, it's invocation is
    automatic from the url mappings.

    :param request: Automatically passed. Contains a map of the httprequest
    :return: A HttpResponse object which is then passed to the browser

    """
    user_id = request.POST.get('user_name')
    if not user_id:
        return HttpResponseRedirect("/") # pragma: no cover
    try:
        # pull out the user from the POST and
        # match it against our db
        user = Tbluser.objects.get(user_id=user_id)
    # if the user doesn't match anything, notify
    except Tbluser.DoesNotExist: # pragma: no cover
        return render_to_response(
            "fail.html",
            {
                "fail": "Login failure",
                "reason":"Non existent user.",
                "helpfultext":"If you expect your account to be " + \
                              "active please contact your manager " + \
                              "or a site administrator."
            },
            RequestContext(request))

    if user.isdisabled():
        return render_to_response(
            "fail.html",
            {
                "fail": "Login failure",
                "reason":"Your account is disabled.",
                "helpfultext":"You will need to request " + \
                              "re-activation from your manager."
            },
            RequestContext(request))

    if user.validate_password(request.POST['password']):
        # if all goes well, send to the tracker
        request.session['user_id'] = user.id

        if user.sup_tl_or_admin():
            return HttpResponseRedirect("/overtime/")
        else:
            return HttpResponseRedirect("/calendar/")
    else:
        return render_to_response(
            "fail.html",
            {
                "fail": "Login failure",
                "reason":"Incorrect password",
                "helpfultext":"You can receive a reminder <a href=\"/" + \
                              "forgot_my_password/\">here</a>"
            },
            RequestContext(request))

def logout(request):

    """Simple logout function

    This function will delete a session id from the session dictionary
    so that the user will need to log back in order to access the same
    pages.

    :param request: Automatically passed contains a map of the httprequest
    :return: A HttpResponse object which is passed to the browser.

    """

    try:
        del request.session['user_id']
    except KeyError:
        pass
    return HttpResponseRedirect("/")

@loggedin
def user_view(request, year=None, month=None, day=None):
    """Generates a calendar based on the URL it receives.  For example:
    domain.com/calendar/{year}/{month}/{day}, also takes a day just in
    case you want to add a particular view for a day, for
    example. Currently a day-level is not in-use.

    :note: The generated HTML should be pretty printed

    :param request: Automatically passed contains a map of the httprequest
    :param year: The year that the view will be rendered with, default is
                 the current year.
    :param month: The month that the view will be rendered with, default is
                  the current month.
    :param day: The day that the view will be rendered with, default is
                the current day

    :returns: A HttpResponse object which is passed to the browser.

    """
    year = datetime.datetime.today().year if year is None else year
    month = datetime.datetime.today().month if month is None else month
    day = datetime.datetime.today().day if day is None else day

    user_id = request.session['user_id']
    calendar_table = gen_calendar(year, month, day,
                                  user=user_id)
    user_object = Tbluser.objects.get(id=user_id)

    return render_to_response(
        'calendar.html',
        {
         'calendar': calendar_table,
         'changeform': EntryForm(),
         'addform': AddForm(),
        },
        RequestContext(request)
    )

@csrf_protect
def ajax(request):

    """Ajax request handler, dispatches to specific ajax functions
    depending on what json gets sent.

    Any additional ajax views should be added to the ajax_funcs map,
    this will allow the dispatch function to be used. Future revisions
    could have a kind of decorator which could be applied to functions
    to mutate some global map of ajax dispatch functions. For now,
    however, just add them into the map.

    The idea for this is that on the client-side call you would
    construct your javascript call with something like the below
    (using jQuery):

        .. code-block:: javascript

           $.ajaxSetup({
               type: 'POST',
               url: '/ajax/',
               dataType: 'json'
           });\n
           $.ajax({
               data: {
                   form: 'functionName',
                   data: 'data'
               }
          });

    Using this method, this allows us to construct a single view url
    and have all ajax requests come through here. This is highly
    advantagious because then we don't have to create a url map and
    construct views to handle that specific call. We just have some
    server-side map and route through there.

    The lookup and dispatch works like this:

    1) Request comes through.
    2) Request gets sent to the ajax view due to the client-side call making a
       request to the url mapped to this view.
    3) The form type is detected in the json data sent along with the call.
    4) This string is then pulled out of the dict, executed and it's response
       sent back to the browser.

    :param request: Automatically passed contains a map of the httprequest
    :return: HttpResponse object back to the browser.

    """

    # see which form we're dealing with and if it's in the POST
    form_type = request.POST.get('form_type', None)

    # if not, try the GET
    if not form_type:
        form_type = request.GET.get('form_type', None)

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
        'profileedit': profile_edit,
        'get_comments': get_comments,
        'add_comment': add_comment,
        'remove_comment': remove_comment,
        'tracking_data': get_tracking_entry_data,
        'password_reminder': forgot_pass,
    }
    try:
        return ajax_funcs.get(
            form_type,ajax_error
            )(request)
    except Exception as e: # pragma: no cover
        error_log.error(str(e))
        raise

@admin_check
def view_with_employee_list(request, template=None, get_all=False): # pragma: no cover
    '''Some pages are generic HTML pages with only a select amount of
    differences on them. We use this to generate the employee select
    box and assign the regularly used template variables for these
    templates.
    '''
    user = Tbluser.objects.get(
        id=request.session.get("user_id", None)
    )

    try:
        ees = user.get_subordinates(get_all=get_all)
        employees_select = generate_employee_box(user, get_all=get_all)
    except tblauth.DoesNotExist:
        ees = []
        employees_select = """<select id=user_select>
                                <option id="null">----------</option>
                              </select>"""

    return render_to_response(
        template,
        {
            "employees": ees,
            "user_form": UserForm(),
            "employee_option_list": employees_select
        },
        RequestContext(request)
    )

@loggedin
def view_with_holiday_list(request,
                           year=None,
                           month=None,
                           process=None,
                           template=None,
                           admin_required=False):
    """Generates the full holiday table for all employees under a manager
    or a user's teammates if they are a regular user.

    :param request: Automatically passed contains a map of the httprequest
    :return: HttpResponse object back to the browser.
    """


    user = Tbluser.objects.get(id=request.session.get('user_id'))

    if admin_required and not user.sup_tl_or_admin():
        raise Http404

    year = datetime.datetime.today().year if year is None else year
    month = datetime.datetime.today().month if month is None else month

    # django urls parse to unicode objects
    year, month = int(year), int(month)

    holiday_table, comments_list, js_calendar = gen_holiday_list(user,
                                                                 year,
                                                                 month,
                                                                 process)

    # calculate the days in the month, this is inefficient.
    # It creates a list of datetime objects and gets the len
    # of that. Being lazy.
    days_this_month = range(1, len(gen_datetime_cal(year, month))+1)

    return render_to_response(
        template,
        {
            'holiday_table': holiday_table,
            'comments_list': comments_list,
            'days_this_month': days_this_month,
            'employee_select': generate_employee_box(user),
            'js_calendar': js_calendar,
        },
        RequestContext(request))

@admin_check
def yearview(request, who=None, year=None): # pragma: no cover
    '''Yearview generates the 'year at a glance' for both Administrators
    and regular users.

    :param who: This will be the ID of an employee which the yearview
    will be generated from if the employee is not within the span
    of control then a 404 will be generated.'''
    auth_user = Tbluser.objects.get(
        id=request.session.get('user_id')
        )

    if not year:
        year = str(datetime.datetime.now().year)
    if not who:
        try:
            userid = auth_user.get_subordinates()[0].id
            return HttpResponseRedirect("/yearview/%s/%s/" % (userid, year))
        except (tblauth.DoesNotExist, IndexError):
            return HttpResponseRedirect("/user_edit/")

    # stop people from editing the URL to access agents outside their
    # span of control.
    try:
        target_user = auth_user.get_subordinates().get(id=who)
    except Tbluser.DoesNotExist:
        raise Http404

    # generate our year table.
    yeartable = target_user.yearview(year)
    # interpolate our values into it.
    yeartable = yeartable.format(employees_select=generate_employee_box(auth_user),
                                 c="EMPTY",
                                 function="")
    return render_to_response("yearview.html",
                              {"yearview_table": yeartable,
                               "year": year,
                               "eeid": who,
                               }, RequestContext(request))

@admin_check
def overtime(request, who=None, year=None):
    auth_user = Tbluser.objects.get(
        id=request.session.get('user_id')
        )
    if not year:
        year = str(datetime.datetime.now().year)
    if not who:
        try:
            userid = auth_user.get_subordinates()[0].id
            return HttpResponseRedirect("/overtime/%s/%s/" % (userid, year))
        except (tblauth.DoesNotExist, IndexError):
            return HttpResponseRedirect("/user_edit/")

    # stop people from editing the URL to access agents outside their
    # span of control.
    try:
        target_user = auth_user.get_subordinates().get(id=who)
    except Tbluser.DoesNotExist:
        raise Http404

    # generate our year table.
    ot_table = target_user.overtime_view(year)
    # interpolate our values into it.
    ot_table = ot_table.format(employees_select=generate_employee_box(auth_user),
                               yearbox=generate_year_box(int(year), id="cmb_yearbox"),
                               c="EMPTY",
                               function="")
    return render_to_response("overtime.html",
                              {"ot_table": ot_table,
                               "year": year,
                               "eeid": who,
                               }, RequestContext(request))

@loggedin
def edit_profile(request):

    """View for sending the user to the edit profile page

    This view is a simple set of fields which allow all kinds of users
    to edit pieces of information about their profile, currently it
    allows uers to edit their name and their password.

    :param request: Automatically passed contains a map of the httprequest
    :return: HttpResponse object back to the browser.

    """

    user = Tbluser.objects.get(id=request.session.get("user_id"))
    return render_to_response("editprofile.html",
                              {'firstname': user.firstname,
                               'lastname': user.lastname,
                               },
                              RequestContext(request))


@loggedin
def explain(request):
    """Renders the Balance explanation page.

    This page renders a simple template to show the users how their
    balance is calculated. This view takes the user object, retrieves
    a couple of fields, which are user.shiftlength and the associated
    values with that datetime object, constructs a string with them
    and passes it to the template as the users 'shiftlength'
    attribute. It then takes the count of working days in the database
    so that the user has an idea of how many days they have tracked
    altogether. Then it calculates their total balance and pushes all
    these strings into the template.

    :param request: Automatically passed contains a map of the httprequest
    :return: HttpResponse object back to the browser.

    """

    user = Tbluser.objects.get(id=request.session.get("user_id"))
    return render_to_response(
        "balance.html",
        {'firstname': user.firstname,
         'lastname': user.lastname,
         'shiftlength': "%s:%s" % (user.shiftlength.hour,
                                   user.shiftlength.minute),
         'working_days': TrackingEntry.objects.filter(user=user.id).count(),
         'balances': user.balance_breakdown(),
         'holiday_balances': user.get_balances(datetime.datetime.now().year),
         },
        RequestContext(request))


def forgot_pass(request):

    """Simple view for resetting a user's password

    This view has a dual function. The first function is to simply
    render the initial page which has a field and the themed
    markup. On this page a user can enter their e-mail address and
    then click submit to have their password sent to them.

    The second function of this page is to respond to the change
    password request. In the html markup of the 'forgotpass.html' page
    you will see that the intention is to have the page post to the
    same URL which this page was rendered from. If the request
    contains POST information then we retrieve that user from the
    database, construct an e-mail based on that and send their
    password to them. Finally, we redirect to the login page.

    :param request: Automatically passed contains a map of the httprequest
    :return: HttpResponse object back to the browser.

    """

    # if the email recipient isn't in the POST dict,
    # then we've got a non-post request
    email_recipient = request.POST.get("email_input", None)
    if not email_recipient:
        return render_to_response("forgotpass.html",
                                  {},
                                  RequestContext(request))

    try:
        try:
            user = Tbluser.objects.get(id=email_recipient)
        except ValueError:
            user = Tbluser.objects.get(user_id=email_recipient)
    except Tbluser.DoesNotExist:
        return render_to_response(
            "fail.html",
            {
                "fail": "Login failure",
                "reason":"Non existent user.",
                "helpfultext":"If you expect your account to be " + \
                "active please contact your manager " + \
                "or a site administrator."
            },
            RequestContext(request))
    user.set_random_password()
    user.send_password_reminder()
    return HttpResponseRedirect("/")
