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
                                              remove_comment)

from timetracker.utils.datemaps import generate_select, generate_employee_box
from timetracker.utils.decorators import admin_check, loggedin
from timetracker.utils.error_codes import CONNECTION_REFUSED
from timetracker.loggers import suspicious_log, email_log, error_log


def index(request):

    """ This function serves the base login page. This view detects if the
    user is logged in. If so, redirects, else, serves them the login page.

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
    if user.is_admin():
        return HttpResponseRedirect("/admin_view/")
    else:
        return HttpResponseRedirect("/calendar/")

def login(request):

    """ This function logs the user in, directly adding the session id to
    a database entry. This function is invoked from the url mapped in urls.py.
    The url is POSTed to, and should contain two fields, the use_name and the
    pass word field. This is then pulled from the database and matched
    against, what the user supplied. If they match, the user is then checked
    to see what *kind* of user their are, if they are ADMIN or TEAML they will
    be sent to the administrator view. Else they will be sent to the user
    page.

    This function shouldn't be directly called, it's invocation is automatic
    from the url mappings.

    :param request: Automatically passed. Contains a map of the httprequest
    :return: A HttpResponse object which is then passed to the browser
    """
   
    try:
        # pull out the user from the POST and
        # match it against our db
        user = Tbluser.objects.get(user_id__exact=request.POST['user_name'])
    # if the user doesn't match anything, notify
    except Tbluser.DoesNotExist:
        return HttpResponse("Username and Password don't match")

    if user.isdisabled():
        raise Http404

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

    """ Simple logout function

    This function will delete a session id from the session dictionary so that
    the user will need to log back in order to access the same pages.

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
    """Generates a calendar based on the URL it receives.
    For example: domain.com/calendar/{year}/{month}/{day},
    also takes a day just in case you want to add a particular
    view for a day, for example. Currently a day-level is not
    in-use.

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
    if year is None:
        year = datetime.datetime.today().year
    if month is None:
        month = datetime.datetime.today().month
    if day is None:
        day = datetime.datetime.today().day


    user_id = request.session['user_id']
    calendar_table = gen_calendar(year, month, day,
                                  user=user_id)

    user_object = Tbluser.objects.get(id=user_id)

    is_admin = user_object.user_type == "ADMIN"
    is_team_leader = user_object.user_type == "TEAML"
    
    balance = user_object.get_total_balance(ret='int')
    return render_to_response(
        'calendar.html',
        {'is_admin': is_admin,
         'is_team_leader': is_team_leader,
         'calendar': calendar_table,
         'changeform': EntryForm(),
         'addform': AddForm(),
         'welcome_name': request.session['firstname'],
         'balance': balance
        },
        RequestContext(request)
        )


def ajax(request):

    """Ajax request handler, dispatches to specific ajax functions depending
    on what json gets sent.

    Any additional ajax views should be added to the ajax_funcs map, this will
    allow the dispatch function to be used. Future revisions could have a kind
    of decorator which could be applied to functions to mutate some global map
    of ajax dispatch functions. For now, however, just add them into the map.

    The idea for this is that on the client-side call you would construct your
    javascript call with something like the below (using jQuery):

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

    Using this method, this allows us to construct a single view url and have
    all ajax requests come through here. This is highly advantagious because
    then we don't have to create a url map and construct views to handle that
    specific call. We just have some server-side map and route through there.

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

    # if the page is accessed via the browser (or other means)
    # we don't serve requests
    if not request.is_ajax():
        raise Http404

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
        'remove_comment': remove_comment
    }
    return ajax_funcs.get(
        form_type,ajax_error
        )(request)

@admin_check
def admin_view(request):

    """This view checks to see if the user logged in is either a team leader or
    an administrator. If the user is an administrator, their authorization
    table entry is found, iterated over to create a select box and it's HTML
    markup, sent to the template. If the user is a team leader, then *their*
    manager's authorization table entry is found and used instead. This is to
    enable team leaders to view and edit the team in which they are on but
    also make it so that we don't explicitly have to duplicate the
    authorization table linking the team leader with their team.

    :param request: Automatically passed contains a map of the httprequest
    :return: HttpResponse object back to the browser.
    """

    # retrieve and assign user object
    auth = Tbluser.objects.get(
        id=request.session.get("user_id", None)
    )

    # if the user is actually a TeamLeader, they can
    # view the team assigned to their manager
    is_team_leader = auth.user_type == "TEAML"
    is_admin = auth.user_type == "ADMIN"
    if is_team_leader:
        auth = auth.get_administrator()

    try:
        employees = tblauth.objects.get(admin=auth)
        employees = employees.users.filter(disabled=False).order_by("lastname")
        ees_tuple = [(user.id, user.name()) for user in employees]
        ees_tuple.append(("null", "----------"))
        employees_select = generate_select(
            ees_tuple,
            id="user_select"
        )
    except tblauth.DoesNotExist:
        employees = []
        employees_select = """<select id=user_select>
                                <option id="null">----------</option>
                              </select>"""

    return render_to_response(
        "admin_view.html",
        {
            "is_admin": is_admin,
            "is_team_leader": is_team_leader,
            "employees": employees,
            'welcome_name': request.session['firstname'],
            'employee_option_list': employees_select
        },
        RequestContext(request)
    )


@admin_check
def add_change_user(request):

    """Creates the view for changing/adding users

    This is the view which generates the page to add/edit/change/remove users,
    the view first gets the user object from the database, then checks it's
    user_type. If it's an administrator, their authorization table entry is
    found then used to create a select box and it's HTML markup. Then pushed
    to the template. If it's a team leader, their manager's authorization
    table is used instead.

    :param request: Automatically passed contains a map of the httprequest
    :return: HttpResponse object back to the browser.
    """

    # retrieve and assign user object
    user = Tbluser.objects.get(
        id=request.session.get("user_id", None)
    )
    is_admin = user.user_type == "ADMIN"
    is_team_leader = user.user_type == "TEAML"
    # get the admin for this user.
    auth = user.get_administrator()
    # since we now will have a manage either way,
    # via the team leader or the actual manager,
    # we get all the users and generate a select
    # option box.
    try:
        auth_links = tblauth.objects.get(admin_id=auth)
        if not is_team_leader:
            ees = auth_links.manager_view()
            ees = list(ees) + [auth]
        else:
            ees = auth_links.teamleader_view()
        ees_tuple = [(user.id, user.name()) for user in ees]
        ees_tuple.append(("null", "----------"))
        employees_select = generate_select(
            ees_tuple,
            id="user_select"
        )
    except tblauth.DoesNotExist:
        ees = []
        employees_select = """<select id=user_select>
                                <option id="null">----------</option>
                              </select>"""

    return render_to_response(
        "useredit.html",
        {
        "employees": ees,
        "user_form": UserForm(),
        'welcome_name': request.session['firstname'],
        'employee_option_list': employees_select,
        'is_team_leader': is_team_leader,
        'is_admin': is_admin
        },
        RequestContext(request)
    )


@loggedin
@admin_check
def holiday_planning(request,
                     year=None,
                     month=None,
                     process=None):
    """
    Generates the full holiday table for all employees under a manager

    First we find the user object and find whether or not that user is a team
    leader or not. If they are a team leader, which set a boolean flag to show
    the template what kind of user is logged in. This is so that the team
    leaders are not able to view certain things (e.g. Job Codes).

    If the admin/tl tries to access the holiday page before any users have
    been assigned to them, then we just throw them back to the main page. This
    is doubly ensuring that they can't access what would otherwise be a
    completely borked page.

    :param request: Automatically passed contains a map of the httprequest
    :return: HttpResponse object back to the browser.
    """
    if year is None:
        year = datetime.datetime.today().year
    if month is None:
        month = datetime.datetime.today().month

    # django urls parse to unicode objects
    year, month = int(year), int(month)

    try:
        user = Tbluser.objects.get(
            id=request.session.get('user_id')
        )
    except Tbluser.DoesNotExist:
        raise Http404

    # if the user is actually a TeamLeader, they can
    # view the team assigned to their manager
    is_team_leader = False
    is_admin = user.user_type == "ADMIN"
    if user.user_type == "TEAML":
        is_team_leader = True
        try:
            user = user.get_administrator()
        except tblauth.DoesNotExist:
            return HttpResponseRedirect("/admin_view/")

    # calculate the days in the month, this is inefficient.
    # It creates a list of datetime objects and gets the len
    # of that. Being lazy.
    days_this_month = range(1, len(gen_datetime_cal(year, month))+1)
    holiday_table, comments_list = gen_holiday_list(user,
                                                    year,
                                                    month,
                                                    process)
    return render_to_response(
        "holidays.html",
        {
            'is_admin': is_admin,
            'holiday_table': holiday_table,
            'comments_list': comments_list,
            'welcome_name': request.session['firstname'],
            'is_team_leader': is_team_leader,
            'days_this_month': days_this_month,
            'employee_select': generate_employee_box(user)
        },
        RequestContext(request))


@admin_check
def yearview(request, who=None, year=None):

    if not year:
        year = str(datetime.datetime.now().year)
    if not who:
        try:
            userid = tblauth.objects.get(
                admin=request.session.get('user_id')
                ).users.filter(disabled=False)[0].id
            return HttpResponseRedirect("/yearview/%s/%s/" % (userid, year))
        except IndexError:
            return HttpResponse("You have no team members.")

    auth_user = Tbluser.objects.get(
        id=request.session.get('user_id')
        )
    is_team_leader = auth_user.user_type == "TEAML"
    is_admin = auth_user.user_type == "ADMIN"
    auth_user = auth_user.get_administrator()
    # stop people from editing the URL to access agents outside their
    # span of control.
    try:
        tblauth.objects.get(admin_id=auth_user).users.get(id=who)
    except Tbluser.DoesNotExist:
        raise Http404

    yeartable = Tbluser.objects.get(id=who).yearview(year)
    yeartable = yeartable.format(employees_select=generate_employee_box(auth_user), c="EMPTY")
    return render_to_response("yearview.html",
                              {"yearview_table": yeartable,
                               "welcome_name": request.session['firstname'],
                               "is_team_leader": is_team_leader,
                               "is_admin": is_admin,
                               "year": year,
                               "eeid": who,
                               }, RequestContext(request))


@loggedin
def edit_profile(request):

    """View for sending the user to the edit profile page

    This view is a simple set of fields which allow all kinds of users to edit
    pieces of information about their profile, currently it allows uers to
    edit their name and their password.

    :param request: Automatically passed contains a map of the httprequest
    :return: HttpResponse object back to the browser.
    """

    user = Tbluser.objects.get(id=request.session.get("user_id"))
    return render_to_response("editprofile.html",
                              {'firstname': user.firstname,
                               'lastname': user.lastname,
                               'welcome_name': request.session['firstname'],
                               'balance': user.get_total_balance(ret='int'),
                               'is_admin': user.user_type == "ADMIN",
                               'is_team_leader': user.user_type == "TEAML"
                               },
                              RequestContext(request))


@loggedin
def explain(request):

    """Renders the Balance explanation page

    This page renders a simple template to show the users how their balance is
    calculated. This view takes the user object, retrieves a couple of fields,
    which are user.shiftlength and the associated values with that datetime
    object, constructs a string with them and passes it to the template as
    the users 'shiftlength' attribute. It then takes the count of working
    days in the database so that the user has an idea of how many days they
    have tracked altogether. Then it calculates their total balance and pushes
    all these strings into the template.

    :param request: Automatically passed contains a map of the httprequest
    :return: HttpResponse object back to the browser.
    """

    user = Tbluser.objects.get(id=request.session.get("user_id"))
    return render_to_response("balance.html",
                              {'firstname': user.firstname,
                               'lastname': user.lastname,
                               'welcome_name': request.session['firstname'],
                               'balance': user.get_total_balance(ret='int'),
                               'shiftlength': str(user.shiftlength.hour) + ': ' + str(user.shiftlength.minute),
                               'working_days': TrackingEntry.objects.filter(user=user.id).count()
                               },
                              RequestContext(request))


def forgot_pass(request):

    """Simple view for resetting a user's password

    This view has a dual function. The first function is to simply render the
    initial page which has a field and the themed markup. On this page a user
    can enter their e-mail address and then click submit to have their
    password sent to them.

    The second function of this page is to respond to the change password
    request. In the html markup of the 'forgotpass.html' page you will see
    that the intention is to have the page post to the same URL which this
    page was rendered from. If the request contains POST information then we
    retrieve that user from the database, construct an e-mail based on that
    and send their password to them. Finally, we redirect to the login page.

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

    # if we're here then the request was a post and we
    # should return the password for the email address
    try:
        user = Tbluser.objects.get(user_id=email_recipient)
        email_message = '''
              Hi {name},
              \tYour password reminder is: {password}\n
              Regards,
              '''.format(**{
                'name': user.name(),
                'password': user.password
                })
        send_mail('You recently requested a password reminder',
                  email_message,
                  'timetracker@unmonitored.com',
                  [email_recipient], fail_silently=False
        )
    except Tbluser.DoesNotExist:
        suspicious_log.info(
            "Someone tried to reset a password of a non-existant address"
        )
    except Exception as error:
        if error[0] == CONNECTION_REFUSED:
            email_log.error("Failed sending e-mail to: %s" % email_recipient)
        else:
            error_log.critical(str(error))
    return HttpResponseRedirect("/")

def reports(request):
    return render_to_response(
        'reports.html',
        {},
        RequestContext(request)
        )

