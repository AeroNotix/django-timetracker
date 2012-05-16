'''
Maps of useful data

Django has this built-in but it is annoying to use
'''

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
    """
    Generates a select box from a tuple of tuples

    i.e.:

    generate_select((
         ('val1', 'Value One'),
         ('val2', 'Value Two'),
         ('val3', 'Value Three')
    ))

    will return:-

    <select id=''>
       <option value="val1">Value One</option>
       <option value="val2">Value Two</option>
       <option value="val3">Value Three</option>
    </select>
    """

    output = []
    out = output.append
    out('<select id="%s">\n' % id)
    for option in data:
        out('\t<option value="%s">%s</option>\n' % (option[0], option[1]))
    out('</select>')
    return ''.join(output)


def pad(string, padchr='0', amount=2):
    """
    Pads a string
    """
    string = str(string)

    if len(str(string)) < amount:
        pre = padchr * (amount - len(string))
        return pre + string

    return string


def float_to_time(timefloat):

    """
    Takes a float and returns the same representation of time
    """
    prefix = ''
    if timefloat < 0:
        timefloat = 0 - timefloat
        prefix = '-'

    minutes = pad(int((60.0 * timefloat) % 60))
    hours = pad(int((60.0 * timefloat) // 60))

    return '%s%s:%s' % (prefix, hours, minutes)
