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

DAYTYPE_CHOICES = (
    ('WKDAY', 'Work Day'),
    ('SICKD', 'Sickness Absence'),
    ('MEDIC', 'Medical Leave'),
    ('SPECI', 'Special Leave'),
    ('SATUR', 'Work on Saturday'),
    ('HOLIS', 'Vacation'),
    ('PUWRK', 'Work on Public Holiday'),
    ('PUABS', 'Public Holiday'),
    ('RETRN', 'Return for Public Holiday'),
    ('WKHOM', 'Work at home'),
    ('TRAIN', 'Training'),
    ('DAYOD', 'Day on demand'),
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
