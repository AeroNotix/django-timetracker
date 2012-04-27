'''
Maps of useful data

Django has this built-in but it's annoying to use
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
    10:('NOV', 'November'),
    11:('DEC', 'December')
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
