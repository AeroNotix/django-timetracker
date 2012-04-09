"""
Module for collecting the utility functions dealing with mostly calendar
tasks, processing dates and creating time-based code.
"""

import datetime
import calendar as cdr

from django.http import Http404

from timetracker.tracker.models import TrackingEntry, Tbluser

MONTH_MAP = {
    0: ('JAN', 'January'),
    1: ('FEB', 'February'),
    2: ('MAR', 'March'),
    3: ('APR', 'April'),
    4: ('MAY', 'May'),
    5: ('JUN', 'June'),
    6: ('JUL', 'July'),
    7: ('AUG', 'August'),
    8: ('SEP', 'September'),
    9: ('OCT', 'October'),
    10:('NOV', 'November'),
    11:('DEC', 'December')
}

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

    if month-1 not in MONTH_MAP.keys():
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


    # need to use authorisation and sessions to get this
    # for testing we'll just grab the same db object
    database = Tbluser.objects.get(user_id__exact=user)

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

    # add our javascript functions
    to_cal("""
           <script type="text/javascript">

              function toggleChangeEntries(st_hour, st_minute, full_st) {
                  $("#starttime").val(full_st);
                  $("#starttime").timepicker("destroy");
                  $("#starttime").timepicker({
                                     hour: st_hour,
                                     minute: st_minute
                                  });
                  $("#starttime").show();
              };

              function hideEntries() {
                  $("#starttime").val('');
              }

           </script>
           """)

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
                                MONTH_MAP[int(month)-1][1]
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
                emptyclass = 'empty-day day-class'
            else:
                emptyclass = 'empty'

            # we've got the month in the query set,
            # so just query that set for individual days
            try:
                # get all the data from our in-memory query-set.
                data = database.get(entry_date__day=_day)
                print str(data.start_time)
                # Use jQuery to change a #comment element to contain the
                # comments for that day.
                to_cal("""\t\t\t\t
                       <td onclick="toggleChangeEntries({0}, {1}, '{2}')"
                           class="{3} day-class">{4}</td>\n""".format(
                                                      data.start_time.hour,
                                                      data.start_time.minute,
                                                      str(data.start_time)[0:5],
                                                      data.daytype,
                                                      _day
                                                     )
                           )

            except TrackingEntry.DoesNotExist:

                to_cal("""\t\t\t\t<td onclick="hideEntries()"
                              class="{0}">{1}</td>\n""".format(emptyclass,
                                                               _day))
        # close up that row
        to_cal("""\t\t\t</tr>\n""")

    # close up the table
    to_cal("""\n</table>""")

    # join up the html and push it back
    return ''.join(cal_html)
