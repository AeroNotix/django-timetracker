'''Django has several of these built-in but they are annoying to use.

:attr:`WEEK_MAP_MID`: This is a map of the days of the week along with the
mid-length string for that value. For example:

.. code-block:: python

   WEEK_MAP_MID = {
       0: 'Mon',
       1: 'Tue',
       ...
   }

:attr:`WEEK_MAP_SHORT`: This is similar except using a longer string.

:attr:`MONTH_MAP`: This is a map of the months which refer to a two-element
tuple which has the short code for the month and the long string for that
month. I.e. 'JAN' and 'January'.

:attr:`MONTH_MAP`: This is a map of the months which refer to a two-element
tuple which has the short code for the month and the long string for that
month. I.e. 'JAN' and 'January'.

:attr:`MONTH_MAP_SHORT`: This is a map of the months which refer to the short
name of a month corresponding to the number. I.e. 1: January.

:attr:`WORKING_CHOICES`: This is a tuple of two-element tuples which contain
the only possible working day possibilites.

:attr:`ABSENT_CHOICES`: This is a tuple of two-element tuples which contain
the only possible absent day possibilities.

:attr:`DAYTYPE_CHOICES`: This is both :attr:`WORKING_CHOICES` and
:attr:`ABSENT_CHOICES` joined together to give all the daytype possibilities.
'''

import datetime

WEEK_MAP_MID = {
    0: 'Mon',
    1: 'Tue',
    2: 'Wed',
    3: 'Thu',
    4: 'Fri',
    5: 'Sat',
    6: 'Sat'
}

WEEK_MAP_SHORT = {
    0: 'Mo',
    1: 'Tu',
    2: 'We',
    3: 'Th',
    4: 'Fr',
    5: 'Sa',
    6: 'Su'
}

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
    10: ('NOV', 'November'),
    11: ('DEC', 'December')
}

MONTH_MAP_SHORT = (
    (1, 'January'),
    (2, 'February'),
    (3, 'March'),
    (4, 'April'),
    (5, 'May'),
    (6, 'June'),
    (7, 'July'),
    (8, 'August'),
    (9, 'September'),
    (10, 'October'),
    (11, 'November'),
    (12, 'December')
)


WORKING_CHOICES = (
    ('WKDAY', 'Work Day'),
    ('SATUR', 'Work on Saturday'),
    ('WKHOM', 'Work at home'),
)

ABSENT_CHOICES = (
    ('HOLIS', 'Vacation'),
    ('SICKD', 'Sickness Absence'),
    ('PUABS', 'Public Holiday'),
    ('SPECI', 'Special Leave'),
    ('RETRN', 'Return for Public Holiday'),
    ('TRAIN', 'Training'),
    ('DAYOD', 'Day on demand'),
)

DAYTYPE_CHOICES = (
    ('WKDAY', 'Work Day'),
    ('HOLIS', 'Vacation'),
    ('SICKD', 'Sickness Absence'),
    ('PUABS', 'Public Holiday'),
    ('PUWRK', 'Work on Public Holiday'),
    ('RETRN', 'Return for Public Holiday'),
    ('SPECI', 'Special Leave'),
    ('TRAIN', 'Training'),
    ('DAYOD', 'Day on demand'),
    ('SATUR', 'Work on Saturday'),
    ('WKHOM', 'Work at home'),
    ('ROVER', 'Return for overtime'),
    ('OTHER', 'Other'),
)

def generate_year_box(year, id=''):
    '''Generates a select box with years -/+ 2 of the year provided.

    :param year: :class:`int` the initial year to start off with.
    :param id: :class:`str` the id attribute to give to the element.
    '''
    year_select_data = [(y, y) for y in range(year, year - 3, -1)]
    year_select_data.extend([(y, y) for y in range(year + 1, year + 3)])
    year_select_data.sort()
    return generate_select(year_select_data, id)

def generate_month_box(id=''):
    '''Generates a select box with months.

    :param id: :class:`str` the id attribute to give to the element.
    '''
    return generate_select(MONTH_MAP_SHORT, id)

def generate_employee_box(admin_user, get_all=False):
    '''Generates a select box with all subordinates for a manager.

    :param admin_user: :class:`timetracker.tracker.models.Tbluser` an instance
                       of a manager who has subordinates underneath them.
    :param get_all: :class:`bool` Used to select or ignore disabled employees.
    '''
    admin_user = admin_user.get_administrator()
    ees = admin_user.get_subordinates(get_all=get_all)
    ees_tuple = [(user.id, user.name()) for user in ees]
    ees_tuple.append(("null", "----------"))
    return generate_select(
        ees_tuple,
        id="user_select"
        )

def generate_select(data, id=''):
    """Generates a select box from a tuple of tuples

    .. code-block:: python

       generate_select((
           ('val1', 'Value One'),
           ('val2', 'Value Two'),
           ('val3', 'Value Three')
       ))

    will return:-

    .. code-block:: html

       <select id=''>
          <option value="val1">Value One</option>
          <option value="val2">Value Two</option>
          <option value="val3">Value Three</option>
       </select>

    :param data: This is a tuple of tuples (can also be a list of lists. But
                 tuples will behave more efficiently than lists and who likes
                 mutation anyway?
    :rtype: :class:`str`/HTML

    """

    output = []
    out = output.append
    out('<select id="%s">\n' % id)
    for option in data:
        out('\t<option value="%s">%s</option>\n' % (option[0], option[1]))
    out('</select>')
    return ''.join(output)


def pad(string, padchr='0', amount=2):
    """Pads a string

    :param string: This is the string you want to pad.
    :param padchr: This is the character you want to pad the string with.
    :param amount: This is the length of the string you want the input end up.
    :rtype: :class:`str`

    """
    string = unicode(string)

    if len(string) < amount:
        pre = padchr * (amount - len(string))
        return pre + string

    return string

def nearest_half(num):
    '''Returns the number rounded down to the nearest half.

    :param n: :class:`int` the number to round
    :return: :class:`float`'''
    return int(round(num / 0.5)) * 0.5

def round_down(num, by_=0.5):
    '''Rounds a number down to the half below'''
    if num < 0:
        return (num // -by_) * -by_
    return (num // by_) * by_

def hr_calculation(user, tracking_days, return_days):
    '''This is the calculation that the HR team use to make overtime
    calculations since the OT calculation cannot take 0.25hr increments
    into account we ignore all those which have 0.25hr -/+ and sum the
    remaining entries together.'''
    total_hours = running_total = 0
    for entry in tracking_days:
        running_total += round_down(entry.total_working_time())
        total_hours += user.shiftlength_as_float()

    for entry in return_days:
        running_total += user.shiftlength_as_float()

    return running_total - total_hours

def float_to_time(timefloat):
    """Takes a float and returns the same representation of time.

    :param timefloat: This is a :class:`float` which needs to be represented
                      as a timestring.
    :rtype: :class:`str` such as '00:12' or '09:15'

    """
    prefix = ''
    if timefloat < 0:
        timefloat = 0 - timefloat
        prefix = '-'

    seconds = timefloat * 3600
    time = prefix + str(datetime.timedelta(seconds=seconds))
    return pad(time[:-3], amount=5)

def datetime_to_timestring(dt_):
    """
    Returns a pretty formatting string from a datetime object.

    For example,
    >>>datetime.time(hour=9, minute=10, second=30)
    ..."09:10:30"

    :param dt_: :class:`datetime.datetime` or :class:`datetime.time`
    :returns: :class:`str`
    """
    return pad(dt_.hour)+':'+pad(dt_.minute)+':'+pad(dt_.second)
