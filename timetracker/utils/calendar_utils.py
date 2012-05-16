"""
Module for collecting the utility functions dealing with mostly calendar
tasks, processing dates and creating time-based code.
"""

import random
import datetime
import calendar as cdr

from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import send_mail
from django.http import Http404, HttpResponse
from django.db import IntegrityError
from django.forms import ValidationError

import simplejson

from timetracker.loggers import (debug_log, info_log,
                                 email_log, database_log,
                                 error_log)
from timetracker.tracker.models import TrackingEntry, Tbluser
from timetracker.tracker.models import Tblauthorization as Tblauth
from timetracker.utils.error_codes import DUPLICATE_ENTRY, CONNECTION_REFUSED
from timetracker.utils.datemaps import MONTH_MAP, generate_select, pad
from timetracker.utils.decorators import (admin_check, json_response,
                                          request_check)


def get_request_data(form, request):

    """
    Given a form and a request object we pull out
    from the request what the form defines.

    i.e.

    form = {
        'data1': None
    }

    get_request_data(form, request) will then fill
    that data with what's in the request object.
    """

    data = dict()

    # get our form data
    for key in form:
        data[key] = request.POST.get(key, None)

    # get the user id from the session
    data['user_id'] = request.session['user_id']

    return data


def validate_time(start, end):

    """
    Validates the times given
    """

    shour, sminute = parse_time(start)
    ehour, eminute = parse_time(end)

    return (datetime.time(shour, sminute)
            < datetime.time(ehour, eminute))


def parse_time(timestring, type_of=int):

    """
    Given a time string will return a tuple of ints,
    i.e. "09:44" returns [9, 44] with the default args,
    you can pass any function to the type argument.
    """

    return map(type_of, timestring.split(":"))


def calendar_wrapper(function):
    """
    Decorator which checks if the calendar function was
    called as an ajax request or not, if so, then the
    the wrapper constructs the arguments for the call
    from the POST items
    """

    def inner(*args, **kwargs):
        """
        Checks argument length and constructs the call
        based on that.
        """

        if isinstance(args[0], WSGIRequest):
            request = args[0]
            try:
                eeid = request.POST.get('eeid', None)
                json_dict = {
                    'success': True,
                    'calendar': function(user=eeid)
                }
                return HttpResponse(simplejson.dumps(json_dict))

            except Exception as e:
                error_log.error(str(e))
                return HttpResponse(str(e))

        else:
            # if the function was called from a view
            # let it just do it's thing
            return function(*args, **kwargs)

    return inner


def gen_holiday_list(admin_user,
                     year=datetime.datetime.today().year,
                     month=datetime.datetime.today().month):

        """
        Outputs a holiday calendar for that month.

        For each user we get their tracking entries,
        then iterate over each of their entries
        checking if it is a holiday or not, if it is
        then we change the class entry for that number
        in the day class' dict.

        Adds a submit button along with passing the
        user_id to it.
        """

        # we convert the arguments to ints because
        # we get given unicode objects
        year, month = int(year), int(month)

        str_output = []
        to_out = str_output.append
        to_out('<table year=%s month=%s id="holiday-table">' % (year, month))
        to_out("""<tr>
                     <th align="centre" colspan="100">{0}</th>
                  </tr>""".format(MONTH_MAP[month - 1][1]))

        # generate the calendar, flatten it and
        # get rid of the zeros
        calendar_array = list()
        for week in cdr.monthcalendar(year, month):
            calendar_array.extend(week)
        calendar_array = filter((lambda x: x > 0), calendar_array)

        for user in admin_user.users.all():
            day_classes = {
                num: 'empty' for num in calendar_array
            }

            # We have a dict with each day as currently
            # empty, we iterate through the tracking
            # entries and apply the daytype from that.
            for entry in user.tracking_entries(year, month):
                day_classes[entry.entry_date.day] = entry.daytype

            # output the table row title, which contains:-
            # Full name, Holiday Balance and the User's
            # job code.
            to_out("""
                   <tr>
                     <th class="user-td">%s</th>
                       <td>%s</td>
                       <td class="job_code">%s</td>""" % (user.name(),
                                                          user.get_holiday_balance(year),
                                                          user.job_code
                                                          )
                   )

            # We've mapped the users' days to the day number,
            # we can write the user_id as an attribute to the
            # table data and also the dayclass for styling,
            # also, the current day number so that the table
            # shows what number we're on.
            for klass, day in day_classes.items():
                to_out('<td usrid=%s class=%s>%s\n' % (user.id, day, klass))

            # user_id is added as attr to make mass calls
            to_out("""<td>
                        <input value="submit" type="button" user_id="{0}"
                               onclick="submit_holidays({0})" />
                      </td>""".format(user.id))
            to_out('</tr>')

        # generate the data for the year select box
        year_select_data = [(y, y) for y in range(year, year - 3, -1)]
        year_select_data.extend([(y, y) for y in range(year + 1, year + 3)])
        year_select_data.sort()

        # generate the data for the month select box
        month_select_data = [(month_num + 1, month[1])
                             for month_num, month in MONTH_MAP.items()]

        # generate the select box for the years
        year_select = generate_select(year_select_data, id="year_select")
        # generate the selecte box for the months
        month_select = generate_select(month_select_data, id="month_select")
        # generate submit all button
        to_out("""
        <tr>
          <td colspan="100" align="right">
            <input id="btn_change_td" value="Reload"
                   type="button"
                   onclick="change_table_data()" />
              {0} {1}
            <input id="submit_all" value="Submit All"
                   type="button"
                   onclick="submit_all()" />
          </td>
         </tr>""".format(year_select, month_select))

        return ''.join(str_output)


@calendar_wrapper
def gen_calendar(year=datetime.datetime.today().year,
                 month=datetime.datetime.today().month,
                 day=datetime.datetime.today().day,
                 user=None):

    """
    Returns a HTML calendar, calling a database user to get their day-by-day
    entries and gives each day a special CSS class so that days can be styled
    individually.

    The generated HTML should be 'pretty printed' as well, so the output code
    should be pretty readable.
    """

    # django passes us Unicode strings
    year, month, day = int(year), int(month), int(day)

    if month - 1 not in MONTH_MAP.keys():
        raise Http404

    # if we've generated December, link to the next year
    if month + 1 == 13:
        next_url = '"/calendar/%s/%s"' % (year + 1, 1)
    else:
        next_url = '"/calendar/%s/%s"' % (year, month + 1)

    # if we've generated January, link to the previous year
    if month - 1 == 0:
        previous_url = '"/calendar/%s/%s"' % (year - 1, 12)
    else:
        previous_url = '"/calendar/%s/%s"' % (year, month - 1)

    # user_id came from sessions or the ajax call
    # so this is pretty safe
    database = Tbluser.objects.get(id__exact=user)

    # pull out the entries for the given month
    try:
        database = TrackingEntry.objects.filter(
            user=database.id,
            entry_date__year=year,
            entry_date__month=month
            )

    except TrackingEntry.DoesNotExist:
        # it seems Django still follows through with the assignment
        # when it raises an error, this is actually quite good because
        # we can treat the query set like normal
        pass

    # create a semi-sparsely populated n-dimensional
    # array with the month's days per week
    calendar_array = cdr.monthcalendar(
        int(year),
        int(month)
    )

    # creating a list holder for the strings
    # this is faster than concatenating the
    # strings as we go.
    cal_html = list()
    to_cal = cal_html.append

    # create the table header
    to_cal("""<table id="calendar" border="1">\n\t\t\t""")

    to_cal("""<tr>
                <td class="table-header" colspan="2">
                  <a class="table-links" href={0}>&lt;</a>
                </td>

                <td class="table-header" colspan="3">{2}</td>

                <td class="table-header" colspan="2">
                  <a class="table-links" href={1}>&gt;</a>
                </td>
              </tr>\n""".format(previous_url,
                                next_url,
                                MONTH_MAP[int(month) - 1][1]
                        )
           )

    # insert day names
    to_cal("""\n\t\t\t<tr>
                <td class=day-names>Mon</td>
                <td class=day-names>Tue</td>
                <td class=day-names>Wed</td>
                <td class=day-names>Thu</td>
                <td class=day-names>Fri</td>
                <td class=day-names>Sat</td>
                <td class=day-names>Sun</td>
              </tr>\n""")

    # each row in the calendar_array is a week
    # in the calendar, so create a new row
    for week_ in calendar_array:
        to_cal("""\n\t\t\t<tr>\n""")

        for _day in week_:

            # the calendar_array fills extraneous days
            # with 0's, we can catch that and treat either
            # end of the calendar differently in the CSS
            if _day != 0:
                emptyclass = 'day-class empty-day'
            else:
                emptyclass = 'empty'

            # we've got the month in the query set,
            # so just query that set for individual days
            try:
                # get all the data from our in-memory query-set.
                data = database.get(entry_date__day=_day)

                # Pass these to the page so that the jQuery functions
                # get the function arguments to edit those elements
                vals = [
                    data.start_time.hour,
                    data.start_time.minute,
                    str(data.start_time)[0:5],
                    data.end_time.hour,
                    data.end_time.minute,
                    str(data.end_time)[0:5],
                    data.entry_date,
                    data.daytype,
                    _day,
                    data.id,
                    data.breaks.minute,
                    str(data.breaks)[0:5]
                    ]

                to_cal("""\t\t\t\t
                       <td onclick="toggleChangeEntries({0}, {1}, '{2}',
                                                        {3}, {4}, '{5}',
                                                        '{6}', '{7}', {9},
                                                        {10}, '{11}')"
                           class="day-class {7}">{8}</td>\n""".format(*vals)
                       )

            except TrackingEntry.DoesNotExist:

                # For clicking blank days to input the day quickly into the
                # box. An alternative to the datepicker
                if _day != 0:
                    entry_date_string = '-'.join(map(pad,
                                                     [year, month, _day]
                                                     )
                                                )
                else:
                    entry_date_string = ''

                # we don't want to write a 0 in the box
                _day = '&nbsp' if _day == 0 else _day

                # write in the box and give the empty boxes a way to clear
                # the form
                to_cal("""\t\t\t\t<td onclick="hideEntries('{0}')"
                    class="{1}">{2}</td>\n""".format(
                                                  entry_date_string,
                                                  emptyclass,
                                                  _day)
                                              )

        # close up that row
        to_cal("""\t\t\t</tr>\n""")

    # close up the table
    to_cal("""\n</table>""")

    # join up the html and push it back
    return ''.join(cal_html)


@request_check
@json_response
def ajax_add_entry(request):

    '''
    Adds a calendar entry asynchronously
    '''

    # object to dump form data into
    form = {
        'entry_date': None,
        'start_time': None,
        'end_time': None,
        'daytype': None,
        'breaks': None
    }

    # get the form data from the request object
    form.update(get_request_data(form, request))

    # create objects to put our data into
    json_data = dict()

    try:
        # server-side time validation
        if not validate_time(form['start_time'], form['end_time']):
            json_data['error'] = "Start time after end time"
            return json_data
    except ValueError:
        error_log.warn("Date error got through - %s and %s" %
                       (form['start_time'], form['end_time']))
        json_data['error'] = "Date Error"
        return json_data

    try:
        entry = TrackingEntry(**form)
        entry.save()
    except IntegrityError as error:
        if error[0] == DUPLICATE_ENTRY:
            database_log.info("Duplicate entry from %s" % form['user_id'])
            json_data['error'] = "There is a duplicate entry for this value"
        else:
            error_log.error(str(error))
            json_data['error'] = str(error)
        return json_data

    year, month, day = map(int,
                           form['entry_date'].split("-")
                           )

    calendar = gen_calendar(year, month, day,
                            form['user_id'])

    # if all went well
    json_data['success'] = True
    json_data['calendar'] = calendar
    return json_data


@request_check
@json_response
def ajax_delete_entry(request):
    """
    Asynchronously deletes an entry
    """

    form = {
        'hidden-id': None,
        'entry_date': None
    }

    # get the form data from the request object
    form.update(get_request_data(form, request))

    # create our json structure
    json_data = {
        'success': False,
        'error': ''
    }

    if form['hidden-id']:
        try:
            # get the user and make sure that the user
            # assigned to the TrackingEntry is the same
            # as what's requesting the deletion
            user = Tbluser.objects.get(id__exact=form['user_id'])
            entry = TrackingEntry(id=form['hidden-id'],
                                  user=user)
            entry.delete()
        except Exception as error:
            error_log.error(str(error))
            json_data['error'] = str(error)
            return json_data

    year, month, day = map(int,
                           form['entry_date'].split("-")
                           )

    calendar = gen_calendar(year, month, day,
                            user=form['user_id'])

    # if all went well
    json_data['success'] = True
    json_data['calendar'] = calendar
    return json_data


@json_response
def ajax_error(error):

    """
    Returns a HttpResponse with JSON as a payload with the error
    code as the string that the function is called with
    """

    return {
        'success': False,
        'error': error
        }


@request_check
@json_response
def ajax_change_entry(request):

    '''
    Changes a calendar entry asynchronously
    '''

    # object to dump form data into
    form = {
        'entry_date': None,
        'start_time': None,
        'end_time': None,
        'daytype': None,
        'breaks': None,
        'hidden-id': None,
    }

    # get the form data from the request object
    form.update(get_request_data(form, request))

    # create objects to put our data into
    json_data = {
        'success': True,
        'error': ''
    }

    try:
        # server-side time validation
        if not validate_time(form['start_time'], form['end_time']):
            json_data['error'] = "Start time after end time"
            return json_data
    except ValueError:
        error_log.error("Date error got through - %s and %s" %
                        (form['start_time'], form['end_time']))
        json_data['error'] = "Date Error"
        return json_data

    if form['hidden-id']:
        try:
            # get the user and make sure that the user
            # assigned to the TrackingEntry is the same
            # as what's requesting the change
            user = Tbluser.objects.get(id__exact=form['user_id'])
            entry = TrackingEntry(id=form['hidden-id'],
                                  user=user)

            # change the fields on the retrieved entry
            entry.entry_date = form['entry_date']
            entry.start_time = form['start_time']
            entry.end_time = form['end_time']
            entry.daytype = form['daytype']
            entry.breaks = form['breaks']

            entry.save()

        except Exception as error:
            error_log.error(str(error))
            json_data['error'] = str(error)
            return json_data

    year, month, day = map(int,
                           form['entry_date'].split("-")
                           )

    calendar = gen_calendar(year, month, day,
                            form['user_id'])

    # if all went well
    json_data['success'] = True
    json_data['calendar'] = calendar
    return json_data


@request_check
@admin_check
@json_response
def get_user_data(request):
    """
    Returns a user as a json object
    """

    user = Tbluser.objects.get(
        id__exact=request.POST.get('user_id', None)
    )

    json_data = {
        'success': False
    }

    if user:

        json_data = {
            'success': True,
            'username': user.user_id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'market': user.market,
            'process': user.process,
            'user_type': user.user_type,
            'start_date': str(user.start_date),
            'breaklength': str(user.breaklength),
            'shiftlength': str(user.shiftlength),
            'job_code': user.job_code,
            'holiday_balance': user.holiday_balance
        }

    return json_data


@request_check
@admin_check
@json_response
def delete_user(request):
    """
    Asynchronously deletes a user
    """

    user_id = request.POST.get('user_id', None)

    json_data = {
        'success': False,
        'error': '',
    }

    if user_id:
        try:
            user = Tbluser.objects.get(id=user_id)
            user.delete()
        except Tbluser.DoesNotExist:
            error_log.error("Tried to delete non-existant user")
            json_data['error'] = "User does not exist"
            return json_data

        json_data['success'] = True
        return json_data
    else:
        json_data['error'] = "Missing user"
    return json_data


@request_check
@admin_check
@json_response
def useredit(request):

    """
    Adds a user to the database asynchronously
    """

    # create a random enough password
    password = ''.join([chr(random.randint(65, 91)) for _ in range(12)])
    data = {'password': password}

    # get the data off the request object
    for item in request.POST:
        if item not in ["form_type", "mode"]:
            data[item] = request.POST[item]

    json_data = {
        'success': False,
        'error': ''
    }

    session_id = request.session.get('user_id')
    try:
        if request.POST.get("mode") == "false":
            # create the user
            user = Tbluser(**data)
            user.save()
            # link the user to the admin
            try:
                # get the user object from the database
                auth_user = Tbluser.objects.get(id=session_id)

                # if the user is a team leader, they don't have
                # table auth instances assigned to them, their
                # manager is the one with the table auth, but
                # the TEAML is assigned the same team.
                if auth_user.user_type == "TEAML":

                    # we find the Tblauth instance with the TEAML user
                    # assigned to it, so we can pull that team
                    auth_user = Tblauth.objects.get(users=session_id).admin

                # Now we have the user with the auth table, get their instance
                auth = Tblauth.objects.get(admin=auth_user)
            except Tblauth.DoesNotExist:
                auth = Tblauth(
                    admin=Tbluser.objects.get(
                    id=session_id))
                auth.save()
            auth.users.add(user)
            auth.save()
            email_message = """
                Hi {0},
                \tYour account has been created with the timetracker.
                Please use the following password to login: {1}.\n
                Regards,
                {2}
                """.format(user.firstname, password, auth_user.firstname)

            send_mail('Your account has been created',
                      email_message,
                      'timetracker@unmonitored.com',
                      [user.user_id],
                      fail_silently=False)
        else:
            # If the mode contains a user_id
            # get that user and update it's
            # attributes with what was on the form
            user = Tbluser.objects.get(id__exact=request.POST.get("mode"))
            for key, value in data.items():
                if key != 'password':
                    setattr(user, key, value)
            user.save()
    except IntegrityError as error:
        if error[0] == DUPLICATE_ENTRY:
            database_log.info("Duplicate entry - %s" % str(error))
            json_data['error'] = "Duplicate entry"
            return json_data
        else:
            database_log.error(str(error))
            json_data['error'] = str(error)
            return json_data
    except ValidationError:
        error_log.error("Invalid data in creating a user")
        json_data['error'] = "Invalid Data."
        return json_data
    except Exception as error:
        if error[0] == CONNECTION_REFUSED:
            email_log.error("email failed to send to %s with manager %s" %
                            (user.user_id, auth.admin.name()))
        else:
            json_data['error'] = str(error)
            error_log.critical(str(error))
            return json_data
    json_data['success'] = True
    return json_data


@request_check
@admin_check
@json_response
def mass_holidays(request):
    """
    Adds a holidays for a specific user en masse
    """

    json_data = {
        'success': False,
        'error': ''
    }

    form_data = {
        'year': None,
        'month': None,
        'user_id': None
    }

    for key in form_data:
        form_data[key] = request.POST.get(key, None)

    holiday_data = simplejson.loads(request.POST.get('holiday_data'))

    for entry in holiday_data.items():

        # conversion to int->str removes newlines easier
        day = str(int(entry[0]))
        year = form_data['year']
        month = form_data['month']
        date = '-'.join([year, month, day])

        if entry[1] == "empty" or (not len(entry[1])):
            try:
                removal_entry = TrackingEntry.objects.get(
                    entry_date=date,
                    user_id=form_data['user_id']
                    )
                removal_entry.delete()
            except TrackingEntry.DoesNotExist:
                """
                because we're sending all data
                with each ajax request, we delete
                ones that are in the database, but
                not in the ajax data, therefore,
                if we get a DoesNotExist it just
                means that we don't need to do
                anything
                """
                pass
        else:
            try:
                # mass uploads are non-working days
                # so the admin doesn't need to assign
                # tonnes of time data to each entry
                time_str = "00:00:00"
                new_entry = TrackingEntry(
                    user_id=form_data['user_id'],
                    entry_date=date,
                    start_time=time_str,
                    end_time=time_str,
                    breaks=time_str,
                    daytype=entry[1]
                    )
                new_entry.save()
            except IntegrityError as error:
                """
                if we find that it's an existant
                entry, it means that we're in change
                mode, so assign the new daytype and save
                """
                if error[0] == DUPLICATE_ENTRY:
                    change_entry = TrackingEntry.objects.get(
                        user_id=form_data['user_id'],
                        entry_date=date
                        )
                    change_entry.daytype = entry[1]
                    change_entry.save()
                else:
                    # if we're here, something real bad has happened
                    # don't send this error to the user
                    error_log.critical(str(error))
                    raise Exception(error)
            except Exception as error:
                # I know this is bad but, we can't allow errors to bubble
                error_log.critical(str(error))
                json_data['error'] = str(error)
                return json_data
    json_data['success'] = True
    return json_data


@request_check
@json_response
def profile_edit(request):
    """
    Asynchronously edits a user's profile
    """

    json_data = {
        "success": False,
        "error": ''
    }

    try:
        # get the user object from the db
        user = Tbluser.objects.get(id=request.session.get("user_id"))
    except Tbluser.DoesNotExist:
        error_log.error("Editing a non-existant user")
        json_data['error'] = "User not found"
        return json_data

    # pull the data out the form
    form_data = get_request_data({
        'firstname': None,
        'lastname': None,
        'password': None
        }, request)
    # get request data also pulls out the user_id,
    # we don't need it
    form_data.pop("user_id")

    # get the items from the form and save them onto the
    # user object
    for key, value in form_data.items():
        setattr(user, key, value)
    user.save()

    json_data['success'] = True
    return json_data
