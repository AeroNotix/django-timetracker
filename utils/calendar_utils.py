"""
Module for collecting the utility functions dealing with mostly calendar
tasks, processing dates and creating time-based code.

Module Functions
++++++++++++++++


=========================  ========================
..                         ..
=========================  ========================
:func:`get_request_data`   :func:`calendar_wrapper`
:func:`validate_time`      :func:`gen_holiday_list`
:func:`parse_time`         :func:`ajax_add_entry`
:func:`ajax_delete_entry`  :func:`ajax_error`
:func:`ajax_change_entry`  :func:`get_user_data`
:func:`delete_user`        :func:`useredit`
:func:`mass_holidays`      :func:`profile_edit`
:func:`gen_datetime_cal`
=========================  ========================
"""

import random
import datetime
import calendar as cdr
from functools import wraps

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
from timetracker.utils.datemaps import (MONTH_MAP, WEEK_MAP_SHORT,
                                        generate_select, pad)
from timetracker.utils.decorators import (admin_check, json_response,
                                          request_check)



def get_request_data(form, request):

    """
    Given a form and a request object we pull out
    from the request what the form defines.

    i.e.::

       form = {
            'data1': None
       }

    get_request_data(form, request) will then fill that data with what's in
    the request object.

    :param form: A dictionary of items which should be filled from
    :param request: The request object where the data should be taken from.
    :returns: A dictionary which contains the actual data from the request.
    :rtype: :class:`dict`
    :raises: KeyError
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
    Validates that the start time is before the end time

    :param start: String time such as "09:45"
    :param end: String time such as "17:00"
    :rtype: :class:`boolean`
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

    :param timestring: String such as '09:44'
    :param type_of: A type which the split string should be converted to,
                    suitable types are: :class:`int`, :class:`str` and
                    :class:`float`.
    """

    return map(type_of, timestring.split(":"))


def calendar_wrapper(function):
    """
    Decorator which checks if the calendar function was
    called as an ajax request or not, if so, then the
    the wrapper constructs the arguments for the call
    from the POST items

    :param function: Literally just gen_calendar.
    :rtype: Nothing directly because it returns gen_calendar's
    """

    @wraps(function)
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

    For each user we get their tracking entries, then iterate over each of
    their entries checking if it is a holiday or not, if it is then we change
    the class entry for that number in the day class' dict. Adds a submit
    button along with passing the user_id to it.

    :param admin_user: :class:`timetracker.tracker.models.Tbluser` instance.
    :param year: :class:`int` of the year required to be output, defaults to
                 the current year.
    :param month: :class:`int` of the month required to be output, defaults to
                 the current month.
    :returns: A partially pretty printed html string.
    :rtype: :class:`str`
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

    # generate the calendar,
    datetime_cal = gen_datetime_cal(year, month)

    # get just the days for the td text
    calendar_array = [day.day for day in datetime_cal]

    # generate the top row, with day names
    day_names = [WEEK_MAP_SHORT[day.weekday()] for day in datetime_cal]
    to_out("""<tr id="theader"><td>Name</td><td>Balance</td><td>Code</td>""")
    [to_out("<td>%s</td>\n" % day) for day in day_names]
    to_out("</tr>")

    # here we add the administrator to their list of employees
    # this means that administrator accounts can view/change
    # their own holidays
    auth_user = Tblauth.objects.get(admin=admin_user.get_administrator())
    if admin_user.user_type == "TEAML":
        user_list = list(auth_user.users.all())
    else:
        user_list = [admin_user] + list(auth_user.users.all())

    comments_list = []
    for user in user_list:
        day_classes = {
            num: 'empty' for num in calendar_array
        }

        # We have a dict with each day as currently
        # empty, we iterate through the tracking
        # entries and apply the daytype from that.
        for entry in user.tracking_entries(year, month):
            day_classes[entry.entry_date.day] = entry.daytype
            if entry.comments:
                comment_string = map(str, [entry.entry_date, entry.user.name(), entry.comments])
                comments_list.append(' '.join(comment_string))

        # output the table row title, which contains:-
        # Full name, Holiday Balance and the User's
        # job code.
        to_out("""
               <tr>
                 <th class="user-td">%s</th>
                   <td>%s</td>
                   <td class="job_code">%s</td>""" % (
            user.name(),
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
    debug_log.debug(comments_list)
    return ''.join(str_output), comments_list


@calendar_wrapper
def gen_calendar(year=datetime.datetime.today().year,
                 month=datetime.datetime.today().month,
                 day=datetime.datetime.today().day,
                 user=None):

    """
    Returns a HTML calendar, calling a database user to get their day-by-day
    entries and gives each day a special CSS class so that days can be styled
    individually.

    How this works is that, we iterate through each of the entries found in the
    TrackingEntry QuerySet for {year}/{month}. Create the table>td for that entry
    then attach the CSS class to that td. This means that each different type of
    day can be individually styled per the front-end style that is required.
    The choice to use a custom calendar table is precisely *because of* this fact
    the jQueryUI calendar doesn't support the individual styling of days, nor does
    it support event handling with the level of detail which we require.

    Each day td has one of two functions assigned to it depending on whether the
    day was an 'empty' day or a non-empty day. The two functions are called:

        .. code-block:: javascript

           function toggleChangeEntries(st_hour, st_min, full_st,
                                        fi_hour, fi_min, full_fi,
                                        entry_date, daytype,
                                        change_id, breakLength,
                                        breakLength_full)
            // and

            function hideEntries(date)


    These two functions could be slightly more generically named, as the calendar
    markup is used in two different places, in the {templates}/calendar.html and
    the {templates}/admin_view.html therefore I will move to naming these based
    on their event names, i.e. 'calendarClickEventDay()' and
    'calendarClickEventEmpty'.

    The toggleChangeEntries() function takes 11 arguments, yes. 11. It's quite
    a lot but it's all the relevant data associated with a tracking entry.

    1) st_hour is the start hour of the tracking entry, just the hour.
    2) st_min is the start minute of the tracking entry, just the minute.
    3) full_st is the full start time of the tracking entry.
    4) fi_hour is the end hour of the tracking entry, just the hour.
    5) fi_min is the end minute of the tracking entry, just the minute.
    6) full_fi is the full end time of the tracking entry.
    7) entry_date is the entry date of the tracking entry.
    8) daytype is the daytype of the tracking entry.
    9) change_id this is the ID of the tracking entry.
    10) breakLength this is the break length's minutes. Such as '15'.
    11) This is the breaklength string such as "00:15:00"

    The hideEntries function takes a single parameter, date which is the date of
    the entry you want to fill in the Add Entry form.

    The generated HTML should be 'pretty printed' as well, so the output code
    should be pretty readable.

    :param year: Integer for the year required for output, defaults to the
                 current year.
    :param month: Integer for the month required for output, defaults to the
                 current month.
    :param day: Integer for the day required for output, defaults to the
                 current day.
    :param user: Integer ID for the user in the database, this will automatically,
                 be passed to this function. However, if you need to use it in
                 another setting make sure this is passed.
    :returns: HTML String
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

    '''Adds a calendar entry asynchronously.

    This method is for RUSERs who wish to add a single entry to their
    TrackingEntries. This method is only available via ajax and obviously
    requires that users be logged in.

    The client-side code which POSTs to this view should contain a json map
    of, for example:

    .. code-block:: javascript

       json_map = {
           'entry_date': "2012-01-01",
           'start_time': "09:00",
           'end_time': "17:00",
           'daytype': "WRKDY",
           'breaks': "00:15:00",
       }


    Consider that the UserID will be in the session database, then we simply
    run some server-side validations and then enter the entry into the db,
    there are also some client-side validation, which is essentially the same
    as here. The redundancy for validation is just *good practice* because of
    the various malicious ways it is possible to subvert client-side
    javascript or turn it off completely. Therefore, redundancy.

    When this view is launched, we create a server-side counterpart of the
    json which is in request object. We then fill it, passing None if there
    are any items missing.

    We then create a json_data dict to store the json success/error codes in
    to pass back to the User and inform them of the status of the ajax
    request.

    We then validate the data. Which involves only time validation.

    The creation of the entry goes like this:
    The form object holds purely the data that the TrackingEntry needs to
    hold, it's also already validated, so, as insecure it looks, it's actually
    perfectly fine as there has been client-side side validation and
    server-side validation. There will also be validation on the database
    level. So we can use \*\*kwargs to instantiate the TrackingEntry and
    .save() it without much worry for saving some erroneous and/or harmful
    data.

    If all goes well with saving the TrackingEntry, i.e. the entry isn't a
    duplicate, or the database validation doesn't fail. We then generate the
    calendar again using the entry_date in the form. We use this date because
    it's logical to assume that if the user enters a TrackingEntry using this
    date, then their calendar will be showing this month.

    We create the calendar and push it all back to the client. The client-side
    code then updates the calendar display with the new data.

    :param request: HttpRequest object.
    :returns: :class:`HttpResponse` object with the mime/application type as
              json.
    :rtype: :class:`HttpResponse`
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
    json_data = {
        'succes': False,
        'error': '',
        'calendar': ''
    }

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
    """Asynchronously deletes an entry

    This method is for RUSERs who wish to delete a single entry from
    their TrackingEntries. This method is only available via ajax
    and obviously requires that users be logged in.

    We then create our json_data map to hold our success status and any
    error codes we may generate so that we may inform the user of the
    status of the request once we complete.

    This part of the code will catch all errors because, well, this is
    production code and there's no chance I'll be letting server 500
    errors bubble to the client without catching and making them
    sound pretty and plausable. Therefore we catch all errors.

    We then take the entry date, and generate the calendar for that year/
    month.

    :param request: :class:`HttpRequest`
    :returns: :class:`HttpResponse` object with mime/application of json
    :rtype: :class:`HttpResponse`
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
        'error': '',
        'calendar': ''
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

    """Returns a HttpResponse with JSON as a payload

    This function is a simple way of instantiating an error when using
    json_functions. It is decorated with the json_response decorator so that
    the dict that we return is dumped into a json object.

    :param error: :class:`str` which contains the pretty
                  error, this will be seen by the user so
                  make sure it's understandable.
    :returns: :class:`HttpResponse` with mime/application of json.
    :rtype: :class:`HttpResponse`
    """

    return {
        'success': False,
        'error': error
        }


@request_check
@json_response
def ajax_change_entry(request):

    '''Changes a calendar entry asynchronously

    This method works in an extremely similar fashion to :meth:`ajax_add_entry`,
    with modicum of difference. The main difference is that in the add_entry
    method, we are simply looking for the hidden-id and deleting it from the
    table. In this method we are *creating* an entry from the form object
    and saving it into the table.

    :param request: :class:`HttpRequest`
    :returns: :class:`HttpResponse` with mime/application of JSON
    :rtype: :class:`HttpResponse`
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
    """Returns a user as a json object.

    This is a very simple method. First, the :class:`HttpRequest` POST is
    checked to see if it contains a user_id. If so, we grab that user from
    the database and take all their relevant information and encode it into
    JSON then send it back to the browser.

    :param request: :class:`HttpRequest` object
    :returns: :class:`HttpRequest` with mime/application of JSON
    :rtype: :class:`HttpResponse`
    """

    json_data = {
        'success': False,
        'error': ''
    }

    try:
        user = Tbluser.objects.get(
            id__exact=request.POST.get('user_id', None)
            )
    except Tbluser.DoesNotExist:
        json_data['error'] = "User does not exist"

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
        json_data['success'] = True

    return json_data


@request_check
@admin_check
@json_response
def delete_user(request):
    """Asynchronously deletes a user.

    This function simply deletes a user. We asynchronously delete the user
    because it provides a better user-experience for the people doing data
    entry on the form. It also allows the page to not have to deal with a
    jerky nor have to create annoying 'loading' bars/spinners.

    :note: This function should not be called directly.

    This function should be POSTed to via an Ajax call. Like so:

    .. code-block:: javascript

       $.ajaxSetup({
           type: "POST",
           url: "/ajax/",       // "ajax" is the url we created in urls.py
           dataType: "json"
       });

       $.ajax({
           data: {
               user_id: 1
           }
       });

    Once this is received, we check that the user POSTing this data is an
    administrator, or at least a team leader and we go ahead and delete the
    user from the table.

    :param request: :class:`HttpRequest`
    :returns: :class:`HttpResponse` mime/application JSON
    :rtype: :class:`HttpResponse`
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
    This function both adds and edits a user

    * Adding a user

    Adding a user via ajax. This function cannot be used outside of an ajax
    request. This is simply because there's no need. If there ever is a need
    to synchronously add users then I will remove the @request_check from the
    function.

    The function shouldn't be called directly, instead, you should POST to the
    ajax view which points to this via :mod:`timetracker.urls` you also
    need to include in the POST data. Here is an example call using jQuery:

    .. code-block:: javascript

       $.ajaxSetup({
           type: "POST",
           dataType: "json"
       });

       $.ajax({
           url: "/ajax/",
           data: {
               'user_id': "aaron.france@hp.com",
               'firstname': "Aaron",
               'lastname': "France",
               'user_type': "RUSER",
               'market': "BK",
               'process': "AR",
               'start_date': "2012-01-01"
               'breaklength': "00:15:00"
               'shiftlength': "00:07:45"
               'job_code': "ABC123"
               'holiday_balance': 20,
               'mode': "false"
           }
       });

    You would also create success and error handlers but for the sake of
    documentation lets assume you know what you're doing with javascript. When
    the function receives this data, it first checks the 'mode' attribute of
    the json data. If it contains 'false' then we are looking at an 'add_user'
    kind of request. Because of this, and the client-side validation that is
    done. We simply use some \*\*kwargs magic on the
    :class:`timetracker.tracker.models.Tbluser` constructor and save our
    Tbluser object.

    Providing that this didn't throw an error and it may, the next step is to
    create a Tblauthorization link to make sure that the user that created
    this user instance has the newly created user assigned to their team (or
    to their manager's team in the case of team leaders). We make the team
    leader check, if it's a team leader we call get_administrator() on the
    authorized user and then save the newly created user into the
    Tblauthorization instance found. Once this has happened we send the user
    an e-mail informing them of their account details and the password that we
    generated for them.

    * Editing a user

    This function also deals with the *editing* of a user instance, it's
    possible that this functionality will be refactored into it's own function
    but for now, we have both in here.

    Editing a user happens much the same as adding a user save for some very
    minor differences:

        .. code-block:: javascript

           $.ajaxSetup({
              type: "POST",
              dataType: "json"
           });

           $.ajax({
               url: "/ajax/",
               data: {
                   'user_id': "aaron.france@hp.com",
                   'firstname': "Aaron",
                   'lastname': "France",
                   'user_type': "RUSER",
                   'job_code': "ABC456"
                   'holiday_balance': 50,
                   'mode': 1
               }
           });

    You may notice that the amount of data isn't the same. When editing a user
    it is not vital that all attributes of the user instance are changed
    and/or sent to this view. This is because of the method used to assign
    back to the user instance the changes of attributes (getattr/setattr).

    The attribute which determines that the call is an edit call and not a add
    user call is the mode, if the mode is not false and is a number.

    When we first step into this function we look for the mode attribute of
    the json data. If it's a number then we look up the user with that user_id
    we then step through each attribute on the request map and assign it to
    the user object which we retrieved from the database.

    :param request: :class:`HttpRequest`
    :returns: :class:`HttpResponse` with mime/application of JSON
    :raises: :class:`Integrity` :class:`Validation` and :class:`Exception`
    :note: Please remember that all exceptions are caught here and to make
           sure that things are working be sure to read the response in the
           browser to see if there are any errors.
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
                            (user.name(), auth.admin.name()))
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
    """Adds a holidays for a specific user en masse

    This function takes a large amount of holidays as json input, iterates
    over them, adding or deleting each one from the database.

    The json data looks as such:

    .. code-block:: javascript

       holidays = {
           1: daytype,
           2: daytype,
           3: daytype
           ...
        }

    And so on, for the entire month. In the request object we also have the
    month and the year. We use this to create a date to filter the month by,
    this is so that we're not deleting/changing the wrong month. The
    year/month are taken from the current table headings on the client. We
    then check what kind of day it is.

    If the daytype is 'empty' then we attempt to retrieve the day mapped to
    that date, if there's an entry, we delete it. This is because when the
    holiday page is rendered it shows whether or not that day is assigned. If
    it was assigned and now it's empty, it means the user has marked it as
    empty.

    If the daytype is *not* empty, then we create a new TrackingEntry instance
    using the data that was the current step of iteration through the
    holiday_data dict. This will be a number and a daytype. We have the user
    we're uploading this for and the year/month from the request object. We
    also choose sensible defaults for what we're not supplied with, i.e. we're
    not supplied with start/end times, nor a break time. This is because the
    holiday page only deals with *non-working-days* therefore we can track
    these days with zeroed times.

    If at this point an IntegrityError is raised, it means one of two things:
    we can either have a duplicate entry, in which case we retrieve that entry
    and change it's daytype, or we can have a different error, in which case
    we wrap up working with this set of data and return an error to the
    browser.

    If all goes well, we mark the return object's success attribute with True
    and return.

    :param request: :class:`HttpRequest`
    :returns: :class:`HttpResponse` with mime/application as JSON
    :note: All exceptions are caught, however here is a list:
    :raises: :class:`IntegrityError` :class:`DoesNotExist`
             :class:`ValidationError` :class:`Exception`
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
    """Asynchronously edits a user's profile.

    Access Level: All

    First we pull out the user instance that is currently logged in. Then as
    with most ajax functions, we construct a map to receive what should be in
    the in the POST object. This view specifically deals with changing a Name,
    Surname and Password. Any other data is not required to be changed.

    Once this data has been populated from the POST object we then retrieve
    the string names for the attributes and use setattr to change them to what
    we've been supplied here.

    :param request: :class:`HttpRequest`
    :returns: :class:`HttpResponse` with mime/application as JSON
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


def gen_datetime_cal(year, month):
    '''Generates a datetime list of all days in a month

    :param year: :class:`int`
    :param month: :class:`int`
    :returns: A flat list of datetime objects for the given month
    :rtype: :class:`List` containing :class:`datetime.datetime` objects.

    '''
    dt = datetime
    days = []
    for week in cdr.monthcalendar(year, month):
        days.extend(week)

    # filter out zeroed days
    days = filter((lambda x: x > 0), days)
    return [dt.datetime(year=year, month=month, day=day) for day in days]

@admin_check
@json_response
def get_comments(request):
    """
    Function which gets the comments from a user's tracking entry
    """

    json_data = {
        'success': False,
        'error': '',
        'comment': ''
    }

    form_data = {
        'user': None,
        'year': None,
        'month': None,
        'day': None
    }

    for key in form_data:
        try:
            form_data[key] = pad(request.GET[key])
        except KeyError:
            json_data['error'] = 'Missing data: %s' % str(key)

    entry_date = "{year}-{month}-{day}".format(**form_data)
    try:
        entry = TrackingEntry.objects.get(entry_date=entry_date,
                                          user_id=form_data['user'])
    except TrackingEntry.DoesNotExist:
        json_data['success'] = True
        return json_data

    json_data['success'] = True
    json_data['comment'] = entry.comments
    return json_data


@admin_check
@json_response
def add_comment(request):
    """
    Function which adds a comment to a tracking entry field.
    """
    json_data = {
        'success': False,
        'error': '',
    }

    form_data = {
        'user': None,
        'year': None,
        'month': None,
        'day': None,
        'comment': None
    }

    for key in form_data:
        try:
            if key in {'month', 'day'}:
                form_data[key] = pad(request.POST[key])
            else:
                form_data[key] = request.POST[key]
        except KeyError:
            json_data['error'] = 'Missing data: %s' % str(key)
    entry_date = "{year}-{month}-{day}".format(**form_data)
    try:
        entry = TrackingEntry.objects.get(entry_date=entry_date,
                                          user_id=form_data['user'])
    except TrackingEntry.DoesNotExist:
        json_data['success'] = False
        json_data['error'] = "No entry to add a comment to!"
        return json_data

    entry.comments = form_data['comment']
    entry.save()
    entry = TrackingEntry.objects.get(entry_date=entry_date,
                                      user_id=form_data['user'])
    json_data['success'] = True
    return json_data


@admin_check
@json_response
def remove_comment(request):
    """
    Function which removes a comment from a tracking field
    """

    json_data = {
        'success': False,
        'error': '',
    }

    form_data = {
        'user': None,
        'year': None,
        'month': None,
        'day': None,
    }

    for key in form_data:
        try:
            form_data[key] = pad(request.POST[key])
        except KeyError:
            json_data['error'] = 'Missing data: %s' % str(key)
    entry_date = "{year}-{month}-{day}".format(**form_data)
    try:
        entry = TrackingEntry.objects.get(entry_date=entry_date,
                                          user_id=form_data['user'])
    except TrackingEntry.DoesNotExist:
        json_data['success'] = True
        return json_data

    entry.comments = ''
    entry.save()
    json_data['success'] = True
    return json_data
