'''Maps of useful data

Django has several of these built-in but they are annoying to use.

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
    ('RETRN', 'Return for Public Holiday'),
    ('SPECI', 'Special Leave'),
    ('TRAIN', 'Training'),
    ('DAYOD', 'Day on demand'),
    ('SATUR', 'Work on Saturday'),
    ('WKHOM', 'Work at home'),
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
    string = str(string)

    if len(str(string)) < amount:
        pre = padchr * (amount - len(string))
        return pre + string

    return string


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
